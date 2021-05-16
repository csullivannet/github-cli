#!/usr/bin/env python3
"""
Author: Christopher Sullivan
Description: A command line tool to get some basic information about a GitHub
repository.
"""

import argparse
import datetime
import dateutil.parser
import json
import os
import pytz
import requests
import sys

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.exceptions import HTTPError

url = f"https://api.github.com/repos"
token = os.environ.get("GITHUB_TOKEN")
auth = {"Authorization": f"Bearer {token}"}
headers = auth


class Session(object):
    def __init__(self, repo, org):
        self.repo = repo
        self.org = org
        self.url = f"{url}/{org}/{repo}/"

    def backoff(self):
        """
        Builds retries with backoff into requests, to help with flaky API
        endpoints. Can help with rate limiting.

        :returns: requests Session object
        """
        s = requests.Session()
        retries = Retry(
            total=5, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504]
        )
        s.mount("https://", HTTPAdapter(max_retries=retries))

        return s

    def get(self, path):
        """
        GETs JSON object from a given API path from the defined url.

        :param path: The API path to retrieve the JSON object
        """

        r = self.backoff().get(self.url + path, headers=headers)
        if r.status_code == 200:
            return r.json()
        else:
            message = (
                f"Request to GitHub using path: {self.url + path} \nreturned: "
                + f"\n{r.json()}"
            )
            raise Exception(message)

    def paginate(self, path):
        """
        Cycles through the paginated GitHub API at a given path on the given url
        to return all possible results. It will append a query for 100 results
        per page (the maximum allowed) and request the next page until no more
        results are returned.

        Will return a list of results concatenated from all of the pages.

        :param path: The API path to request from
        """
        more_pages = True
        api_path = path + "?per_page=100&page="
        page = 1
        results = []

        while more_pages:
            path = api_path + str(page)
            r = self.get(path)
            results.extend(r)
            page += 1
            if not r:
                more_pages = False

        return results

    def get_prs(self, target):
        """
        Gets a list of all open PRs aginst the specified target. Gets all open
        PRs against all targets when the target is 'open'.

        :param target: The branch against which has open PRs.
        :param org: The GitHub organization to check.
        :param repo: A repo in the above organization to check.

        :returns: The information for each PR, as a list of JSON objects
                  returned by GitHub.
        """
        pulls = self.paginate("pulls")
        prs = []
        for pr in pulls:
            if target == "open":
                prs.append(pr)
            elif pr["base"]["ref"] == target:
                prs.append(pr)

        return prs


def time_difference(date):
    insertion_date = dateutil.parser.parse(date)
    difference = pytz.utc.localize(datetime.datetime.utcnow()) - insertion_date
    return difference


def output(pr, verbose):
    if verbose:
        return pr
    else:
        output = {"url": pr["url"], "owner": pr["user"]["login"]}
        return output


def arguments():
    """
    A handler for command line arguments.
    :returns: arguments passed at the command line.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--repo",
        "-r",
        nargs="+",
        help="MANDATORY. Repository or repositories to query.",
        required=True,
    )

    parser.add_argument(
        "--org",
        "-o",
        help="MANDATORY. Organization the repositor{y|ies} belongs to.",
        required=True,
    )

    parser.add_argument(
        "--max-age",
        "-m",
        help="Maximum age of pr(s) queried, in days.",
    )

    parser.add_argument(
        "--labels",
        "-l",
        nargs="+",
        help="Inclusive or match of any provided labels.",
    )

    parser.add_argument(
        "--all-labels",
        "-L",
        action="store_true",
        help="All provided labels must be present, but ignores any extras.",
    )

    parser.add_argument(
        "--file",
        "-f",
        help="Path to write output to file.",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print all data retrieved from pr(s).",
    )

    return parser.parse_args()


def main():
    """
    Where things get done.
    """

    if not token:
        print("GITHUB_TOKEN not present! Quitting!")
        sys.exit(1)

    args = arguments()
    max_age = int(args.max_age) if args.max_age is not None else None
    labels = set(args.labels)
    all_labels = args.all_labels
    verbose = args.verbose
    filepath = args.file

    prs = []
    filtered_prs = []

    for repo in args.repo:
        s = Session(repo, args.org)
        prs.extend(s.get_prs("open"))

    for pr in prs:
        # No labels set, but max age set
        if max_age and not labels:
            if time_difference(pr["created_at"]) < datetime.timedelta(days=max_age):
                filtered_prs.append(output(pr, verbose))

        # Labels set, but not max age
        elif not max_age and labels:
            s = set((i["name"]) for i in pr["labels"])
            if all_labels and labels.issubset(s):
                filtered_prs.append(output(pr, verbose))
            elif not all_labels and labels.intersection(s):
                filtered_prs.append(output(pr, verbose))

        # Labels set and max age set
        elif max_age and labels:
            if time_difference(pr["created_at"]) < datetime.timedelta(days=max_age):
                s = set((i["name"]) for i in pr["labels"])
                if all_labels and labels.issubset(s):
                    filtered_prs.append(output(pr, verbose))
                elif not all_labels and labels.intersection(s):
                    filtered_prs.append(output(pr, verbose))

    if not filepath:
        print(filtered_prs)
    else:
      with open(filepath, "w", encoding="utf8") as json_file:
          json.dump(filtered_prs, json_file)


if __name__ == "__main__":
    """
    To allow being called as a script, if installing as a CLI is not desired.
    """
    main()
