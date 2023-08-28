#!/bin/bash
set -exo pipefail

# This is the config we have in the wiki encoded by configs_from_env
DEFAULT_CONFIG="H4sIAH9rQGQC/3WRUW+CMBSF/wrpiy9Ctz3yhtBsTKMG4WFZl6bAlXTiraPdzG\
L87wOJRjS7T037nXPvPT0QuVO0qBWgFQaKBqzxPo1G4jvkwNHpipMVm0fPSRyJYBmLKXvj7TMnnIzv\
ie7AkjPA8ciRjJ2+jca1qrxfua07e9d1OW4BrMJKFFrXpd6j2ANsjO88PnCMgjSYBCsmsmQmlski8p\
2R+aqVBZ+2tdfNxuxkAYbmINFQr1KWKlxrWkorc2nA6/ERx+5G7Br9o0poWv/3j36udaPRApa0Vvl5\
wJv9OVkEWfryJMJZzOapiKN2O05OPV0Lxrp9fq4qL4ncalYsTFj6j67P/UobzhZZJCZZOD1pnIEo/y\
42A/riPeTuXNsEX1l4B54/6fgHlibBbwwCAAA="

YELP_BEANS_CONFIG=$DEFAULT_CONFIG python .devcontainer/configs_in_env.py load_from_env

make development

# Test API
pushd api
make serve &
# Give time for the server to start
sleep 20
curl 'http://localhost:5000/'
popd

# Test Frontend
pushd frontend
make serve &
# Give time for the server to start
sleep 30
curl 'http://localhost:8080'
popd

api/venv/bin/pre-commit run --all-files
