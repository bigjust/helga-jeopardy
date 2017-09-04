# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.3.14] - 2017-09-04
### Fixed
- re-add settings.CHANNELS check
- all customization or omission of channel announcement

## [0.3.13] - 2017-07-09
### Fixed
- confer with settings.CHANNELS before doing anything

## [0.3.12] - 2017-04-01
### Fixed
- use question_id to query questions (novel idea, i know)

## [0.3.11] - 2017-03-31
### Added
- reset command
### Fixed
- don't use question text for mongo queries

## [0.3.10] - 2017-03-21
### Fixed
- unicode issues (hopefully)

## [0.3.9] - 2017-03-11
### Added
- added title to leaderboard
- score subcommand 'all' which will show the all time leaderboard

## [0.3.8] - 2017-03-02
### Fixed
- Missing import for RequestException (stupid stupid stupid)

## [0.3.7] - 2017-03-02
### Fixed
- handle exceptions from the trivialbuzz api

## [0.3.6] - 2016-11-21
### Fixed
- answers with parenthesis are detected and match accordingly

## [0.3.5] - 2016-11-21
### Fixed
- formatting currency properly in scoreboard

## [0.3.4] - 2016-11-21
### We're just not going to talk about this one

## [0.3.3] - 2016-11-20
### Fixed
- syntax error

## [0.3.2] - 2016-11-20
### Fixed
- fixed quoting in usage

## [0.3.1] - 2016-11-20
### Fixed
- issue with leaderboard and requesting nick

## [0.3.0] - 2016-11-20
### Added
- top 3 players in last week, and requesting user's score

## [0.2.4] - 2016-11-20
### Changed
- track timestamp of answer, for date range-based leaderboards

## [0.2.3] - 2016-11-20
### Changed
- track who answers question correctly

## [0.2.2] - 2016-11-20
### Changed
- remove stopwords from answer tokens before evaling

## [0.2.1] - 2016-11-13
### Added
- ratio threshold to answer evaluation
- debug logging

## [0.2.0] - 2016-10-27
### Added
- adding hooks so other plugins can run jeopardy type games

### Fixed
- unicode tokens now parse correctly


## [0.1.3] - 2016-10-25
useless version bump


## [0.1.2] - 2016-10-23
### Added
- tracks active questions per channel
- allow multiple correct responses
- improve matching, introduce partial response ('can you be more specific?')

## [0.1.1] - 2016-10-23
- attempts to determine if a person answered correct


## [0.1.0] - 2016-10-16
### Added
- can query random questions from api, reveals answer 1 min (by default) later
