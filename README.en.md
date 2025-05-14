# AltPlan

[![en](https://img.shields.io/badge/lang-en-blue.svg)](https://github.com/GrzybowskiBYD/AltPlan/blob/main/README.en.md)
[![pl](https://img.shields.io/badge/lang-pl-red.svg)](https://github.com/GrzybowskiBYD/AltPlan/blob/main/README.md)

Altplan is a program that interprets timetable data and then presents it in an accessible form of a website.

---
Altplan was created for students and teachers who use the original - unreadable and feature-poor - [timetable page](https://plan.zse.bydgoszcz.pl) on a daily basis.

Altplan introduces many conveniences and features including:
1. Overlay of substitutions on the schedule
2. Dark theme and choice of theme color
3. Dedicated mobile version
4. Time of the last update
5. Lucky Number field
6. Many other minor improvements

The finished site can be seen at [altplan.zse.bydgoszcz.pl](https://altplan.zse.bydgoszcz.pl).

## Installation

To install Altplan:
1. Make sure Docker is installed 
2. (Optional) create a fork of the repository
3. Clone the repository
4. Use the command `docker compose -f .\docker-compose.yml up` or follow [documentation](https://docs.docker.com/reference/cli/docker/compose/#examples)
5. Done! Altplan should be available at [localhost:80](http://localhost:80)