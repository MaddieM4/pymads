#!/bin/bash

pylint pymads/*.py \
    --include-ids=y \
    --disable=W0142 # * or ** magic. Great and legitimate feature.
