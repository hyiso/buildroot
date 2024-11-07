#!/usr/bin/env python3
#
# Copyright (c) 2012 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Prints locally available SDK to standard output.

Usage:
  python find_sdk.py
"""

import logging
import os
import sys

def find(path, search, results):
  if not path or not os.path.exists(path):
    return
  for item in os.listdir(path):
    cur_path = os.path.join(path, item)
    if os.path.isdir(cur_path):
      if cur_path.endswith(search):
        results.append(os.path.abspath(cur_path))
      find(cur_path, search, results)

def isValidNdkPath(path):
  if not path:
    return False
  dirs = [
    os.path.join(path),
    os.path.join(path, "sysroot"),
    os.path.join(path, "llvm", "bin"),
    os.path.join(path, "build-tools", "cmake", "bin"),
  ]
  for dir in dirs:
    if not os.path.exists(dir):
      return False
  return True

def getNdkHome():
  OHOS_NDK_HOME = os.getenv("OHOS_NDK_HOME")
  if not OHOS_NDK_HOME:
    dirs = []
    find(os.getenv("OHOS_SDK_HOME"), "native", dirs)
    find(os.getenv("DEVECO_SDK_HOME"), "native", dirs)
    dirs.sort(reverse=True)
    for dir in dirs:
      if isValidNdkPath(dir):
        OHOS_NDK_HOME = dir
        break
  logging.info("OHOS_NDK_HOME = %s" % OHOS_NDK_HOME)
  if not isValidNdkPath(OHOS_NDK_HOME):
    logging.error(
      """
  Please set the environment variables for HarmonyOS SDK to "DEVECO_SDK_HOME".
  We will use both native/llvm and native/sysroot.
  Please ensure that the file "native/llvm/bin/clang" exists and is executable."""
    )
    exit(10)
  return OHOS_NDK_HOME

def main():
    OHOS_NDK_HOME = getNdkHome()
    print(OHOS_NDK_HOME)
    return 0


if __name__ == '__main__':
  sys.exit((main()))