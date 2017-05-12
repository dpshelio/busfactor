from functools import reduce
import sys
import git
import glob
from astropy.table import Table
from tqdm import tqdm
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
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

def piechart(total, unique):
    labels = ['ok', 'no ok']
    fig1, ax1 = plt.subplots()
    ax1.pie([total, unique], labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.show()

def plot_topusers(author_commits, author_lastdate):

    colors_author = np.array([author_lastdate[x] for x in author_commits['author']])
    colors_author_orig = colors_author
    colors_author = colors_author / colors_author.max()
    norm = colors.Normalize(colors_author.min(), colors_author.max())
    color = [cm.viridis(norm(ca)) for ca in colors_author]

    fig = plt.figure()
    ax = fig.add_axes([0.2, 0.2, 0.65, 0.7])
    #fig, ax = plt.subplots()
    #import pdb; pdb.set_trace()
    # Example data
    y_pos = np.arange(len(author_commits))

    ax.barh(y_pos, author_commits['commits'], align='center',
            color=color, ecolor='black')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(author_commits['author'])
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Files')
    ax.set_title('Authors')

    ax1 = fig.add_axes([0.2, 0.05, 0.65, 0.08])
    cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=cm.viridis,
                                    norm=colors.Normalize(colors_author_orig.min()/365., colors_author_orig.max()/365.),
                                    orientation='horizontal')
    plt.show()

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
        last_date = subprocess.check_output(("git log --author='{}' --pretty=format:'%cd' "
                                             "| head -n1").format(author), shell=True)
        date_diff = (datetime.datetime.today() -
                     datetime.datetime.strptime(last_date.decode()[:-7],
                                                "%a %b %W %H:%M:%S %Y"))
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
              dtype=('S100','S100', 'i4', 'S10' ))
    t.convert_bytestring_to_unicode()
    for file_i in tqdm(files[:300]):
        row = analyse_file(file_i, git.Repo())
        if row:
            t.add_row([file_i] + row)

    t.sort(['last date','filename'])
    t.write('{}_critic.txt'.format(sys.argv[1]), format='ascii.fixed_width', overwrite=True)
    piechart(len(files), len(t))
    authors_commit = topusers(t, top=None)
    author_dict = get_last_commit_of(authors_commit['author'])
    plot_topusers(authors_commit, author_dict)
    print(author_commit)

# What else I want to do?
## DONE:sort table by date
## DONE: Find last commit from these critic authors (are they still contributing?)
## DONE: Plot pie chart with files vs unique // also in lines of code?
## DONE: Plot user ranking vs files (lines of code)
## ALOMST DONE:Accept list of files to ignore, e.g.: __init__.py, setup_package.py, ...
## TODO: Set up so it downloads repo (from user/repo in github or URL), and runs it all, and create slide/report
