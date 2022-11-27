import os
import datetime


def idata2schemaorg(filename, data, settings):
    info = os.stat(filename)
    # print(data)
    spatial_coverage = get_spatial_coverage(data)
    print("spatial_coverage" + str(spatial_coverage))
    creator = get_creator(data)
    identifier = get_identifier_list(data)

    schemaorg_json = {
        "@context": "https://schema.org",
        "@id": os.path.basename(filename),  # should be a url
        "sameAs": "link",
        "url": "link",

        "@type": "Dataset",
        "additionalType": "link",
        "name": os.path.basename(filename),
        # "description": read_head(filename, settings),
        "keywords": ["Keyword1", "Keyword2", "Keyword3"],

        "creativeWorkStatus": "Published",

        # "inLanguage": "en-US",

        "identifier": identifier,

        "creator": creator,

        "temporalCoverage": "2018-05-24/2018-06-24",

        "spatialCoverage": spatial_coverage,

        "publisher": {
            "@type": "Organization",
            "name": "Publisher Name"
        },

        "provider": {
            "@id": "provider id",
            "@type": "Organization",
            "name": "Yiqing Qu",
            "url": ""
        },
        "includedInDataCatalog": {
            "@type": "DataCatalog",
            "name": "GeoEDF",
            "url": "link"
        },

        "license": {
            "@type": "CreativeWork",
            "text": "This resource is shared under the Creative Commons Attribution CC BY.",
            "url": "http://creativecommons.org/licenses/by/4.0/"
        },

        "isAccessibleForFree": True,
        "dateModified": datetime.datetime.fromtimestamp(info.st_mtime).isoformat(),
        "datePublished": datetime.datetime.fromtimestamp(info.st_mtime).isoformat(),
        "subjectOf": {
            "@type": "DataDownload",
            "name": "resourcemetadata.xml",
            "description": "Description about the dataset",
            "url": "link",
            "encodingFormat": "application/rdf+xml"
        },
    }

    return schemaorg_json


def get_spatial_coverage(data):
    if data is None:
        return None

    spatial_data_fields = ['southlimit', 'westlimit', 'northlimit', 'eastlimit', ]
    # spatial_data_fields = ['latmin', 'lonmin', 'latmax', 'lonmax', ]
    # todo lat lon
    for field in spatial_data_fields:
        if field not in data:
            return None

    box = '%f %f %f %f' % (
        # data['latmin'], data['lonmin'], data['latmax'], data['lonmax'])
        data['southlimit'], data['westlimit'], data['northlimit'], data['eastlimit'])

    return {  # todo: two kinds of coverage, point/shape
        "@type": "Place",
        "geo": {
            "@type": "GeoShape",
            "box": box
        }
    }


def get_identifier_list(data):
    if data is None:
        return None
    identifier = {
        "@type": "PropertyValue",  # todo 了解property value
    }
    if "identifier" in data:
        identifier['filename'] = data['identifier']
    if "id" in data:
        identifier['@id'] = data['id']
    if "url" in data:
        identifier['url'] = data['url']
    return [identifier]


def get_creator(data):
    if data is None:
        return None
    return {
        "@list": [
            {
                "@type": "Person",
                "affiliation": {
                    "@type": "Organization",
                    "name": "Test Affiliation Name"
                },
                "email": "affliation@gmail.com",
                "name": "Test Creator Name",
                "url": "user's profile link"
            }
        ]
    }
