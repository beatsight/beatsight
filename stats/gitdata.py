import os
import fnmatch

import pygit2 as git

def get_file_extension(filepath: str):
    assert filepath
    filename = os.path.basename(filepath)
    basename_parts = filename.split('.')
    if len(basename_parts) == 1:
        # 'folder/filename'-case
        return filename.lower()
    elif len(basename_parts) == 2 and not basename_parts[0]:
        # 'folder/.filename'-case
        return filename.lower()
    else:
        # "normal" case
        return basename_parts[-1].lower()

def map_signature(mailmap, signature):
    # the unmapped email is used on purpose
    email = signature.email
    try:
        mapped_signature = mailmap.resolve_signature(signature)
        name = mapped_signature.name
    except ValueError:
        name = signature.name
        if not name:
            name = "Empty Empty"
            # warnings.warn(f"{str(e)}. Name will be replaced with '{name}'")
        if not email:
            email = "empty@empty.empty"
            # warnings.warn(f"{str(e)}. Email will be replaced with '{email}'")
    return name, email

def is_file_ignored(file_path, ignore_patterns):
    """
    Check if a file or directory should be ignored based on the provided ignore patterns.

    Args:
        file_path (str): The absolute path of the file or directory.
        ignore_patterns (list): A list of ignore patterns.

    Returns:
        bool: True if the file or directory should be ignored, False otherwise.
    """
    for pattern in ignore_patterns:
        if pattern.startswith("!"):
            if fnmatch.fnmatch(file_path, pattern[1:]):
                return False
        elif fnmatch.fnmatch(file_path, pattern):
            return True
    return False

def gen_commit_record(repo, commit, ignore_patterns=[]):
    mailmap = git.Mailmap.from_repository(repo)
    author_name, author_email = map_signature(mailmap, commit.author)

    is_merge_commit = False
    insertions, deletions = 0, 0
    corrected_insertions, corrected_deletions = 0, 0
    details = {
        'A': [],
        'D': [],
        'M': [],
        'R': [],
    }
    file_exts = set()
    if len(commit.parents) == 0:  # initial commit
        diff = commit.tree.diff_to_tree(swap=True)
        st = diff.stats
        insertions, deletions = st.insertions, st.deletions
        corrected_insertions, corrected_deletions = st.insertions, st.deletions

        for patch in diff:
            added_lines = 0
            deleted_lines = 0

            for hunk in patch.hunks:
                for line in hunk.lines:
                    if line.origin == '+':
                        added_lines += 1
                    elif line.origin == '-':
                        deleted_lines += 1

            if is_file_ignored(patch.delta.new_file.path, ignore_patterns):
                corrected_insertions -= added_lines
                corrected_deletions -= deleted_lines

            op = patch.delta.status_char()
            details[op].append({
                'file_path': patch.delta.new_file.path,
                'insertions': added_lines,
                'deletions': deleted_lines,
            })
            file_exts.add(get_file_extension(patch.delta.new_file.path))

    elif len(commit.parents) == 1:
        parent_commit = commit.parents[0]
        diff = repo.diff(parent_commit, commit)
        diff.find_similar()

        st = diff.stats
        insertions, deletions = st.insertions, st.deletions
        corrected_insertions, corrected_deletions = st.insertions, st.deletions

        for patch in diff:
            added_lines = 0
            deleted_lines = 0

            for hunk in patch.hunks:
                for line in hunk.lines:
                    if line.origin == '+':
                        added_lines += 1
                    elif line.origin == '-':
                        deleted_lines += 1

            if is_file_ignored(patch.delta.new_file.path, ignore_patterns):
                corrected_insertions -= added_lines
                corrected_deletions -= deleted_lines

            op = patch.delta.status_char()
            if op == 'R':
                details[op].append({
                    'old_file_path': patch.delta.old_file.path,
                    'file_path': patch.delta.new_file.path,
                    'insertions': added_lines,
                    'deletions': deleted_lines,
                })
            else:
                details[op].append({
                    'file_path': patch.delta.new_file.path,
                    'insertions': added_lines,
                    'deletions': deleted_lines,
                })
            file_exts.add(get_file_extension(patch.delta.new_file.path))

    # case len(commit.parents) > 1 corresponds to a merge commit
    # merge commits are ignored: changes in merge commits are normally because of integration issues
    else:
        is_merge_commit = True

    return {
        'commit_sha': str(commit.id),
        'commit_msg': commit.message,
        'is_merge_commit': is_merge_commit,
        'author_name': author_name,
        'author_email': author_email,
        'author_tz_offset': commit.author.offset,
        'author_timestamp': commit.author.time,
        'author_datetime': commit.author.time,
        'insertions': insertions,
        'deletions': deletions,
        'corrected_insertions': corrected_insertions,
        'corrected_deletions': corrected_deletions,
        'details': details,
        'file_exts': list(file_exts),
    }
