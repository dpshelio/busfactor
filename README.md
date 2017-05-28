BUSSSSSSSSSSSSS

After installing it with `pip install -e .` you can run it as:

```bash
$ cd project_repo
$ buss project_lib
```

This produces three files:
- `project_repo_critic.txt` with the list of files of only one contributor
- a piechart with the % of these files in `project_repo_total.png`
- a bar plot showing the number of files per author coloured by the
time passed since their last commit.

See at some examples at the
[blog post where I talk about this](http://dpshelio.github.io/blog/2017/05/28/fortran-in-scipy-or-the-bus-factor-in-some-python-projects.html)
