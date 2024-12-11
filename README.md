# Beatsight

[English](README.md) | [简体中文](README.zh.md)

Beatsight is a comprehensive project and developer activity tracking tool designed to provide clear insights into development progress and contributions. It features a GitHub-like activity calendar (heatmap) that visualizes project and developer contributions over time, offering an intuitive way to track engagement.

![](https://i.imgur.com/agUmzJc.png)

The platform aggregates commit records from all projects and displays them on the homepage in an easy-to-understand timeline format, highlighting contributions and progress across multiple projects. Detailed project information is provided, including programming languages used, contributors, and a complete record of commit activity.

![](https://i.imgur.com/VB1Ed0B.png)

For developers, Beatsight offers a detailed view of their contributions, including the programming languages they use, the projects they have contributed to, and their commit activity. The tool allows for intuitive comparisons and the export of development activity data across multiple projects and developers, including commit counts, code changes, and other key metrics, helping to analyze and understand contributions comprehensively.

Beatsight enables teams and organizations to gain a deeper understanding of development activities, making it easier to manage and optimize project workflows.

## Demo

You can try out Beatsight on our demo site: [Beatsight Demo](https://demo.beatsight.com/accounts/demo/)


## Features

- Connect GitHub, GitLab, or other Git platforms to perform incremental data analysis, enabling real-time tracking and analysis of project changes and contributions.

- GitHub-like activity calendar(heatmap) designed to visualize project and developer contributions over time.

- Aggregate commit records from all projects and present them on the homepage in an intuitive timeline format, clearly showcasing contributions and progress across projects.

- Project details include programming languages used, contributors, and a detailed record of commit activity.

- Developer details include programming languages, contributed projects, and commit activity.

- Intuitively compare and export development activity data for multiple projects and developers, including commit count, code changes, and other key metrics, to comprehensively analyze contributions.

## Contributing

Bug reports and feature requests as well as pull requests are welcome. To contribute:

1. Fork the repository

2. Create a new branch (git checkout -b feature-branch)

3. Make your changes

4. Commit your changes (git commit -am 'Add new feature')

5. Push to the branch (git push origin feature-branch)

6. Create a new pull request


## Development

To run Beatsight in development mode, follow these steps:

1. Clone the repositories:

   ```bash
   git clone https://github.com/beatsight/beatsight.git
   git clone https://github.com/beatsight/beatsight-web.git
   ```

2. Install backend dependencies and run:

    ```
    cd beatsight
    pip install -r requirements-dev.txt
    python3 manage.py runserver 0.0.0.0:8081
    ```

3. Install frontend dependencies and run:

    ```
    cd beatsight-web
    yarn
    npm run start
    ```


## LICENSE

Beatsight is licensed under the GNU General Public License v3.0 (GPL v3). See the [LICENSE](LICENSE) file for more details.

This project includes components from [repostat](https://github.com/vifactor/repostat), licensed under the GNU General Public License v3.0. See [licenses/LICENSE-repostat](licenses/LICENSE-repostat) for details.

## Copyright (C) 2024-2025 Beatsight Ltd.

All rights reserved.

Portions of this project include code derived from repostat, licensed under the GNU General Public License v3.0.


## Acknowledgements

- [repostat](https://github.com/vifactor/repostat) - Used for Git repository analyse.

- [gitstat](https://github.com/hoxu/gitstats) - Inspired by this project, we have adapted and expanded its functionality to better meet our needs.

- [duckdb](https://duckdb.org/) - A lightweight yet powerful analytical database that helps us efficiently perform data analysis.
