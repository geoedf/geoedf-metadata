import datetime
import fnmatch
import hashlib
import json
import os
import re
import shutil

import click
import ruamel.yaml
from identify import identify

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


def filename2dict(filename, settings):
    # print(json.dumps(filename))
    info = os.stat(filename)
    schemaorg_json_obj = metadata2schemaorg(filename, settings)
    schemaorg_json_obj_static = metadata2schemaorg_static(filename, settings)
    return {
        "tags": file_tags(filename),
        "extension": extension(filename),
        "head": read_head(filename, settings),
        "name": os.path.basename(filename),
        "relpath": filename,
        **stat_dict(filename),
        "identifier": os.path.basename(filename),
        "title": os.path.basename(filename),
        "dateCreated": datetime.datetime.fromtimestamp(info.st_mtime).isoformat(),
        "dateModified": datetime.datetime.fromtimestamp(info.st_mtime).isoformat(),
        "description": read_head(filename, settings),

        # "subject": filename,

        # schemaorg json
        "schemaorgJson": schemaorg_json_obj,
        # "schemaorgJson": schemaorg_json_obj,
        # "creator": {
        #     "@list": [
        #         {
        #             "@type": "Person",
        #             "affiliation": {
        #                 "@type": "Organization",
        #                 "name": "CEOS"
        #             },
        #             "email": "nxgeilfus@gmail.com",
        #             "name": "Nicolas-XavierGeilfus",
        #             "url": "https://www.hydroshare.org/user/10458/"
        #         }
        #     ]
        # },

    }


def metadata2schemaorg(filename, settings):
    rsp = extract_metadata(filename)
    return {
        "key": "value",
    }


def metadata2schemaorg_static(filename, settings):
    return {
        "@context": "https://schema.org",
        "@id": "https://doi.org/10.4211/hs.a3c0d38322fc46ea96ecea2438b29283#schemaorg",
        "sameAs": "https://www.hydroshare.org/resource/a3c0d38322fc46ea96ecea2438b29283",
        "url": "https://doi.org/10.4211/hs.a3c0d38322fc46ea96ecea2438b29283",

        "@type": "Dataset",
        "additionalType": "http://www.hydroshare.org/terms/CompositeResource",
        "name": os.path.basename(filename),
        "description": read_head(filename, settings),
        "keywords": ["Greenhouse gases", "landfast", "Sea ice", "Gas"],

        "creativeWorkStatus": "Published",

        "inLanguage": "en-US",

        # todo
        # "identifier": [
        #     {
        #         "filename": os.path.basename(filename),
        #         "@id": "https://doi.org/10.4211/hs.a3c0d38322fc46ea96ecea2438b29283",
        #         "@type": "PropertyValue",
        #         "propertyID": "https://registry.identifiers.org/registry/doi",
        #         "url": "https://doi.org/10.4211/hs.a3c0d38322fc46ea96ecea2438b29283",
        #         "value": "doi:10.4211/hs.a3c0d38322fc46ea96ecea2438b29283"
        #     },
        #     "https://www.hydroshare.org/resource/a3c0d38322fc46ea96ecea2438b29283"
        # ],

        "creator": {
            "@list": [
                {
                    "@type": "Person",
                    "affiliation": {
                        "@type": "Organization",
                        "name": "CEOS"
                    },
                    "email": "nxgeilfus@gmail.com",
                    "name": "Nicolas-Xavier Geilfus",
                    "url": "https://www.hydroshare.org/user/10458/"
                }
            ]
        },

        "temporalCoverage": "2014-05-24/2014-06-24",

        "spatialCoverage": {
            "@type": "Place",

            "name": "Young Sound",

            "geo": {
                "@type": "GeoCoordinates",
                "latitude": 74.3185,
                "longitude": -20.3364

            }
        },

        "publisher": {
            "@id": "https://www.hydroshare.org"
        },

        "provider": {
            "@id": "https://www.hydroshare.org",
            "@type": "Organization",
            "name": "HydroShare",
            "url": "https://www.hydroshare.org"
        },
        "includedInDataCatalog": {
            "@type": "DataCatalog",
            "name": "HydroShare",
            "url": "https://www.hydroshare.org/search/"
        },

        "license": {
            "@type": "CreativeWork",

            "text": "This resource is shared under the Creative Commons Attribution CC BY.",
            "url": "http://creativecommons.org/licenses/by/4.0/"

        },

        "isAccessibleForFree": True,

        "datePublished": "2022-09-14T17:35:27.897468+00:00",
        "subjectOf": {
            "@type": "DataDownload",
            "name": "resourcemetadata.xml",
            "description": "Dublin Core Metadata Document Describing the Dataset",
            "url": "https://www.hydroshare.org/hsapi/resource/a3c0d38322fc46ea96ecea2438b29283/scimeta/",
            "encodingFormat": "application/rdf+xml"
        },
        # "distribution": {
        #     "@type": "DataDownload",
        #     "contentSize": "48.0 KB",
        #     "encodingFormat": "application/zip",
        #     "contentUrl": "https://www.hydroshare.org/hsapi/resource/a3c0d38322fc46ea96ecea2438b29283/",
        #     "description": "Zipped BagIt Bag containing the HydroShare Resource",
        #     "dateModified": "2022-09-14T17:35:31.297816+00:00",
        #
        #     # "identifier": [
        #     #     "https://www.hydroshare.org/resource/a3c0d38322fc46ea96ecea2438b29283",
        #     #     {
        #     #         "@type": "PropertyValue",
        #     #         "additionalType": [
        #     #             "http://www.wikidata.org/entity/Q185235",
        #     #             "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions/md5"
        #     #         ],
        #     #         "identifier": "md5:788e75d9228abceb6f9f8bae66e58463",
        #     #         "propertyID": "MD5",
        #     #         "value": "788e75d9228abceb6f9f8bae66e58463"
        #     #     }
        #     # ]
        # },
    }


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
    default="data/files",
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
    for filename in all_filenames("."):
        rendered_data[filename] = filename2dict(filename, settings)

    os.chdir(old_cwd)
    for filename, data in rendered_data.items():
        with open(target_file(output, filename), "w") as fp:
            prettyprint_json(data, fp)

    click.echo("metadata extraction complete")
    click.echo(f"results visible in\n  {output}")
