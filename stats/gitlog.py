"""
This file is part of Beatsight.

Copyright (C) 2024-2025 Beatsight Ltd.
Licensed under the GNU General Public License v3.0.
"""
## git log --numstat --pretty=format:'--%H--%ad--%aN--%ae--%s--%P' --date=iso-strict > git_log.txt

import os
import re
import fnmatch
from datetime import datetime
from beatsight.utils.git import log_num_stat

def gen_commit_record(repo_path, since_commit=None, exclude_patterns=[]):
    file_path = log_num_stat(repo_path, since_commit=since_commit)
    data = parse_git_log(file_path, exclude_patterns)
    os.remove(file_path)
    return data

def parse_git_log(file_path, exclude_patterns=[]):
    commits = []
    current_commit = None

    with open(file_path, 'r') as file:
        for line in file:
            # Check for commit details line
            if line.startswith("--"):
                # If there's an existing commit, append it to the list
                if current_commit:
                    current_commit['file_exts'] = list(current_commit['file_exts'])
                    commits.append(current_commit)

                # Parse commit details
                parts = line.strip().split("--")
                commit_sha = parts[1]
                commit_msg = parts[5]
                parents = parts[6].split() if len(parts) > 6 else []
                is_merge_commit = len(parents) > 1
                author_name = parts[3]
                author_email = parts[4]
                author_datetime = parts[2]

                # Parse datetime and timezone
                try:
                    timestamp = datetime.fromisoformat(author_datetime.replace("Z", "+00:00"))
                    tz_offset = timestamp.utcoffset().total_seconds() // 60 if timestamp.utcoffset() else 0
                except ValueError:
                    timestamp = datetime.strptime(author_datetime, "%Y-%m-%dT%H:%M:%S")
                    tz_offset = 0  # Default to UTC if no timezone information

                # Initialize commit dictionary with details field
                current_commit = {
                    'commit_sha': commit_sha,
                    'commit_msg': commit_msg,
                    'is_merge_commit': is_merge_commit,
                    'author_name': author_name,
                    'author_email': author_email,
                    'author_tz_offset': int(tz_offset),
                    'author_timestamp': int(timestamp.timestamp()),
                    # 'author_datetime': author_datetime,
                    'author_datetime': int(timestamp.timestamp()),
                    'insertions': 0,
                    'deletions': 0,
                    'corrected_insertions': 0,
                    'corrected_deletions': 0,
                    'file_exts': set(),
                    'details': {
                        'A': [],  # Added files
                        'D': [],  # Deleted files
                        'M': [],  # Modified files
                        'R': []   # Renamed files
                    },
                }
            else:
                # Parse file changes (insertions and deletions)
                match = re.match(r'(\d+)\s+(\d+)\s+(.+)', line)
                if match and current_commit:
                    added, removed, file_path = match.groups()
                    added, removed = int(added), int(removed)

                    # Handle rename case (detected by '=>')
                    if '=>' in file_path:
                        # Rename detected, split old and new file paths
                        # old_path, new_path = file_path.split(' => ')
                        change_type = 'R'  # File renamed
                    elif added == 0 and removed == 0:
                        # TODO: No way to determin add/delete an empty file.
                        change_type = 'M'
                    elif added > 0 and removed == 0:
                        change_type = 'A'  # File added
                    elif removed > 0 and added == 0:
                        change_type = 'D'  # File deleted
                    else:
                        change_type = 'M'  # File modified

                    # Update total insertions and deletions for the commit
                    current_commit['insertions'] += added
                    current_commit['deletions'] += removed

                    # Check if the file should be excluded based on the patterns
                    if any(fnmatch.fnmatch(file_path, pattern) for pattern in exclude_patterns):
                        ...     # do nothing
                    else:
                        current_commit['corrected_insertions'] += added
                        current_commit['corrected_deletions'] += removed

                    current_commit['details'][change_type].append({
                        'file_path': file_path,
                        'insertions': added,
                        'deletions': removed,
                    })

                    # Extract file extension and add to the set
                    if '.' in file_path:
                        file_ext = file_path.split('.')[-1].lower()  # Convert extension to lowercase
                        file_ext = file_ext.rstrip('}')
                        current_commit['file_exts'].add(file_ext)

        # Append the last commit
        if current_commit:
            current_commit['file_exts'] = list(current_commit['file_exts'])
            commits.append(current_commit)

    return commits
