#!/usr/bin/env python3

TEST_PAYLOAD = [
  (
    {"repos_url": "https://api.github.com/orgs/google/repos"},
    [
      {"name": "episodes.dart", "license": {"key": "bsd-3-clause"}},
      {"name": "cpp-netlib", "license": {"key": "bsl-1.0"}},
      {"name": "dagger", "license": {"key": "apache-2.0"}},
      {"name": "ios-webkit-debug-proxy", "license": {"key": "other"}},
      {"name": "google.github.io", "license": None},
      {"name": "kratu", "license": {"key": "apache-2.0"}},
      {"name": "build-debian-cloud"},
      {"name": "traceur-compiler", "license": {"key": "apache-2.0"}},
      {"name": "firmata.py", "license": {"key": "apache-2.0"}},
    ],
    ['episodes.dart', 'cpp-netlib', 'dagger', 'ios-webkit-debug-proxy', 'google.github.io', 'kratu', 'build-debian-cloud', 'traceur-compiler', 'firmata.py'],
    ['dagger', 'kratu', 'traceur-compiler', 'firmata.py'],
  )
]
