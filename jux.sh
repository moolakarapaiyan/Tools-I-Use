#!/bin/bash
#javascript url extractor
#cat example.js | jux

grep -o -E "(https?://)?/?[{}a-z0-9A-Z_\.-]{2,}/[{}/a-z0-9A-Z_\.-]+"
