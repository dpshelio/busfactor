from functools import reduce
import sys
import os
import git
import glob
from astropy.table import Table
from tqdm import tqdm
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.ticker as ticker
import subprocess
import datetime


def analyse_file(filename, repo):

    commits = repo.iter_commits(paths=filename)

    allcommits = [c for c in commits]
    if len(allcommits) == 0:
        return None
    authors = set()
    for commit in allcommits:
        authors.add(commit.author.name)
        if len(authors) > 1:
            return None
    commits_number = len(allcommits)
    return [str(authors.pop()), commits_number, "{:%Y-%m-%d}".format(allcommits[0].authored_datetime)]


def piechart(total, unique, project):
    labels = ['ok', 'no ok']
    fig1, ax1 = plt.subplots()
    ax1.set_title("{}".format(project))
    ax1.pie([total, unique], labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    fig1.tight_layout()
    fig1.savefig("{}_total.png".format(project))


def plot_topusers(author_commits, author_lastdate, project):

    colors_author = np.array([author_lastdate[x] for x in author_commits['author']]) / 365
    color_max = 1 if colors_author.max() < 1 else colors_author.max()
    colors_author = colors_author / color_max
    color = [cm.viridis(ca) for ca in colors_author]

    fig = plt.figure()
    ax = fig.add_axes([0.30, 0.25, 0.65, 0.65])
    # Example data
    ax.set_title("{}".format(project))
    if len(author_commits) > 5:
        y_pos = np.arange(len(author_commits))
        y_lab = author_commits['author']
        ax.barh(y_pos, author_commits['commits'], align='center',
                color=color, ecolor='black')
    else:
        n = 5 - len(author_commits)
        y_pos = np.arange(5)
        y_lab = [' '] * n + [a for a in author_commits['author']]
        ax.barh(y_pos[n:], author_commits['commits'], align='center',
                color=color, ecolor='black')


    if max(author_commits['commits']) < 10:
        tick_spacing = 2
        ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_lab)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('# Files')
    maxcommits = max(author_commits['commits'])
    ax.set_xlim(0, maxcommits + 0.5 if maxcommits > 5 else 5.5)
    ax.set_title(project)
    ax1 = fig.add_axes([0.30, 0.1, 0.65, 0.05])
    cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=cm.viridis,
                                    norm=colors.Normalize(0, color_max),
                                    orientation='horizontal', label='Years')
    ax1.set_title
    fig.savefig("{}_authors.png".format(project))


def topusers(table, top=5):
    # Aggregate by authors
    authorg = table.group_by('author')
    authorsums = authorg.groups.aggregate(len)
    authorsums.sort(['commits'])

    if top is not None:
        top = top * -1
    people = authorsums[top:]

    return people


def get_last_commit_of(authors):
    author_dict = dict()
    for author in authors:
        author_git = author
        if os.path.exists(".mailmap"):
            author_git = subprocess.check_output("grep '{}' .mailmap".format(author) +
                                                 "| awk -F'<' '{print $1}'| head -n1", shell=True)
            # it comes with a `\n` - why??
            author_git = author_git.strip().decode()

            # check if this name returns anything, if not use previous name
            if author_git == '':
                author_git = author
        last_date = subprocess.check_output(("git log --use-mailmap --author='{}' --date=iso --pretty=format:'%cd' "
                                             "| head -n1").format(author_git), shell=True)
        date_diff = (datetime.datetime.today() -
                     datetime.datetime.strptime(last_date.decode()[:19],
                                                "%Y-%m-%d  %H:%M:%S"))
        author_dict[author] = date_diff.days
    return author_dict


def main():
    files = reduce(lambda l1, l2: l1 + l2,
                   [glob.glob(sys.argv[1] + "/**/*." + e, recursive=True)
                    for e in ['py', 'f', 'c', 'h', 'pyx']])
    not_wanted = ['__init__.py', 'setup_package.py']
    files = [f for f in files if f.split('/')[-1] not in not_wanted]
    t = Table([[], [], [], []],
              names=('filename', 'author', 'commits', 'last date'),
              dtype=('S100', 'S100', 'i4', 'S10'))
    t.convert_bytestring_to_unicode()
    gitrepo = git.Repo()
    project = gitrepo.working_dir.split(os.sep)[-1]
    for file_i in tqdm(files):
        row = analyse_file(file_i, gitrepo)
        if row:
            t.add_row([file_i] + row)

    t.sort(['last date', 'filename'])
    t.write('{}_critic.txt'.format(project), format='ascii.fixed_width', overwrite=True)
    piechart(len(files), len(t), project)
    authors_commit = topusers(t, top=None)
    author_dict = get_last_commit_of(authors_commit['author'])
    plot_topusers(authors_commit, author_dict, project)
    print(authors_commit)

# What else I want to do?
## DONE:sort table by date
## DONE: Find last commit from these critic authors (are they still contributing?)
## DONE: Plot pie chart with files vs unique // also in lines of code?
## DONE: Plot user ranking vs files (lines of code)
## ALOMST DONE:Accept list of files to ignore, e.g.: __init__.py, setup_package.py, ...
## TODO: Set up so it downloads repo (from user/repo in github or URL), and runs it all, and create slide/report
