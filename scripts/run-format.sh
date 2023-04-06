#!/usr/bin/env bash

cd "${0%/*}/.."

find . -regex '.*\.\(c\|cpp\|cc\|cxx\|h\|hpp\)' -not -path "./CppParser/*" -not -path "./common/*" -exec clang-format -style=file -i {} \;