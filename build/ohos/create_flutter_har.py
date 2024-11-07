#!/usr/bin/env python3
#
# Copyright (c) 2023 Hunan OpenValley Digital Industry Development Co., Ltd.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Create a HAR incorporating all the components required to build a Flutter application"""

import argparse
import logging
import os
import re
import shutil
import subprocess
import sys

def runGitCommand(command):
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        raise Exception(f"Git command failed: {result.stderr}")
    return result.stdout.strip()

# 执行命令
def runCommand(command, cwd=None):
    logging.info("runCommand start, command = %s" % (command))
    code = subprocess.Popen(
        command,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
    ).wait()
    if code != 0:
        logging.error("runCommand error, code = %s, command = %s" % (code, command))
        exit(code)
    else:
        logging.info("runCommand finish, code = %s, command = %s" % (code, command))


# 编译har文件，通过hvigorw的命令行参数指定编译类型(debug/release/profile)
def buildHar(buildDir, buildType):
    runCommand("hvigorw GenerateBuildProfile", cwd=buildDir)
    runCommand(
        "hvigorw clean --mode module "
        + "-p module=flutter@default -p product=default -p buildMode=%s " % buildType
        + "assembleHar --no-daemon",
        cwd=buildDir,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build_dir", help="Path to build.")
    parser.add_argument(
        "--build_type",
        choices=["debug", "release", "profile"],
        help="Type to build flutter.har.",
    )
    parser.add_argument("--output", help="Path to output flutter.har.")
    parser.add_argument("--native_lib", action="append", help="Native code library.")
    parser.add_argument("--ohos_abi", help="Native code ABI.")
    parser.add_argument("--source_dir", help="Path to sources.", type=str)
    parser.add_argument("--source_files", help="Path to sources.", type=str, nargs="+")
    options = parser.parse_args()

    root_build_dir = os.path.join(options.build_dir, "flutter_embedding")
    if os.path.exists(root_build_dir):
        shutil.rmtree(root_build_dir)
    os.makedirs(root_build_dir)

    # copy sources files
    for file in options.source_files:
        sourceFile = os.path.join(options.source_dir, file)
        targetFile = os.path.join(options.build_dir, file)
        targetDir = os.path.dirname(targetFile)
        if not os.path.exists(targetDir):
            os.makedirs(targetDir)
        shutil.copyfile(sourceFile, targetFile)

    # copy so files
    for file in options.native_lib:
        targetDir = os.path.join(root_build_dir, "flutter/libs", options.ohos_abi)
        if not os.path.exists(targetDir):
            os.makedirs(targetDir)
        shutil.copyfile(file, os.path.join(targetDir, os.path.basename(file)))
    buildHar(root_build_dir, options.build_type)
    shutil.copyfile(
        os.path.join(
            root_build_dir, "flutter/build/default/outputs/default/flutter.har"
        ),
        options.output,
    )


if __name__ == "__main__":
    sys.exit(main())
