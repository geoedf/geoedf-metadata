import datetime
import fnmatch
import hashlib
import json
import os
import re
import shutil
import uuid

import click
import ruamel.yaml
from identify import identify

from .extract.converter import idata2schemaorg
from .extract.extract_metadata import extract_metadata
from .lib import all_filenames, common_options, prettyprint_json

yaml = ruamel.yaml.YAML(typ="safe")


def file_tags(filename):
    return list(identify.tags_from_path(filename))


def stat_dict(filename):
    info = os.stat(filename)
    return {
        "mode": oct(info.st_mode),
        "size_bytes": info.st_size,
        "mtime": datetime.datetime.fromtimestamp(info.st_mtime).isoformat(),
    }


def extension(filename):
    if "." in filename:
        return filename.split(".")[-1]
    return None


def read_head(filename, settings):
    match = False
    for pattern in settings.read_head["files"]:
        if fnmatch.fnmatch(filename, pattern):
            match = True

    if not match:
        return None

    # read 2x the desired length of data (to handle preamble matches below)
    #
    # note that this is not necessarily 'head_length' bytes
    # e.g. if the file is encoded in utf-8, 1 character can be up to 4 bytes
    with open(filename) as fp:
        data = fp.read(settings.head_length * 2)
    # once the data is read, check it against any skip_preamble_patterns to see
    # if there is a match
    # and if so, take data starting after that match
    for pattern in settings.skip_preamble_patterns:
        match = pattern.search(data)
        if match:
            return data[match.end():][: settings.head_length]
    # if there was no match, truncate down to the correct length
    return data[: settings.head_length]


def get_basic_info(filename, settings):
    info = os.stat(filename)

    return {
        "tags": file_tags(filename),
        "extension": extension(filename),
        "name": os.path.basename(filename),
        "identifier": os.path.basename(filename),
        "title": os.path.basename(filename),
        "dateCreated": datetime.datetime.fromtimestamp(info.st_mtime).isoformat(),
        "dateModified": datetime.datetime.fromtimestamp(info.st_mtime).isoformat(),
        "description": read_head(filename, settings),
    }


def filename2dict(filename, settings):
    print("\n===========\nfilename: " + filename)
    info = os.stat(filename)
    file_uuid = str(uuid.uuid4())
    schemaorg_json_obj = metadata2schemaorg(filename, file_uuid, settings)
    # schemaorg_json_obj_static = metadata2schemaorg_static(filename, settings)
    return {
        "relpath": filename,
        **stat_dict(filename),
        "head": read_head(filename, settings),
        "tags": file_tags(filename),
        "extension": extension(filename),
        "name": os.path.basename(filename),
        "identifier": file_uuid,
        "title": os.path.basename(filename),
        "dateCreated": datetime.datetime.fromtimestamp(info.st_mtime).isoformat(),
        "dateModified": datetime.datetime.fromtimestamp(info.st_mtime).isoformat(),
        "description": read_head(filename, settings),
        "basicInfo": get_basic_info(filename, settings),
        "subject": file_uuid,
        # schemaorg json
        "schemaorgJson": schemaorg_json_obj,
    }


def metadata2schemaorg(filename, file_uuid, settings):
    metadata = extract_metadata(filename)
    print(json.dumps(metadata))

    return idata2schemaorg(filename, metadata, file_uuid, settings)


def target_file(output_directory, filename):
    hashed_name = hashlib.sha256(filename.encode("utf-8")).hexdigest()
    os.makedirs(output_directory, exist_ok=True)
    return os.path.join(output_directory, hashed_name) + ".json"


class Settings:
    def __init__(self, settingsdict):
        self.read_head = settingsdict.get("read_head", {})
        if "files" not in self.read_head:
            self.read_head["files"] = []
        self.head_length = int(self.read_head["length"])
        patterns = self.read_head.get("skip_preamble_patterns", [])
        self.skip_preamble_patterns = [re.compile(p) for p in patterns]


def _load_settings_callback(ctx, param, value):
    if value is not None:
        with open(value) as fp:
            return Settings(yaml.load(fp))


@click.command(
    "extract",
    help="Extract metadata from a directory.\n"
         "This command creates per-file metadata from a directory of files. "
         "Stat data like mode and mtime, the first 100 characters, and the "
         "detected filetype are all used",
)
@click.option(
    "--directory",
    default="data/files/group",
    show_default=True,
    help="A path, relative to the current working directory, "
         "containing data files from which to extract metadata",
)
@click.option(
    "--clean",
    default=False,
    is_flag=True,
    help="Empty the output directory before writing any data there",
)
@click.option(
    "--output",
    default="output/extracted",
    show_default=True,
    help="A path, relative to the current working directory, "
         "where the extracted metadata should be written",
)
@click.option(
    "--settings",
    default="data/config/extractor.yaml",
    show_default=True,
    callback=_load_settings_callback,
    help="YAML file with configuration for the extractor",
)
@common_options
def extract_cli(settings, directory, output, clean):
    if clean:
        shutil.rmtree(output, ignore_errors=True)

    old_cwd = os.getcwd()
    os.chdir(directory)

    rendered_data = {}
    # in all_filenames("single_files")
    for filename in all_filenames("."):
        # name, ext = os.path.splitext(filename)
        # print(name + ", " + ext + ".")

        rendered_data[filename] = filename2dict(filename, settings)

    # in all_filenames("multiple_files")
    # generate schemaorg for each file
    # generate schemaorg for the zip file
    # add schemaorg of each file to the 'hasPart' field in the schemaorg of the zip file


    os.chdir(old_cwd)
    for filename, data in rendered_data.items():
        with open(target_file(output, filename), "w") as fp:
            prettyprint_json(data, fp)

    click.echo("metadata extraction complete")
    click.echo(f"results visible in\n  {output}")
