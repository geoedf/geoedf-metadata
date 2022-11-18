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
        "keywords": ["Greenhouse gases", "landfast", "Sea ice", "Gas"],

        "creativeWorkStatus": "Published",

        # "inLanguage": "en-US",

        "identifier": identifier,

        "creator": creator,

        "temporalCoverage": "2014-05-24/2014-06-24",

        "spatialCoverage": spatial_coverage,

        "publisher": {
            "@type": "Organization",
            "name": "Publisher Name"
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
        "dateModified": datetime.datetime.fromtimestamp(info.st_mtime).isoformat(),
        "datePublished": datetime.datetime.fromtimestamp(info.st_mtime).isoformat(),
        "subjectOf": {
            "@type": "DataDownload",
            "name": "resourcemetadata.xml",
            "description": "Dublin Core Metadata Document Describing the Dataset",
            "url": "https://www.hydroshare.org/hsapi/resource/a3c0d38322fc46ea96ecea2438b29283/scimeta/",
            "encodingFormat": "application/rdf+xml"
        },
    }

    return schemaorg_json


def get_spatial_coverage(data):
    if data is None:
        print(1)
        return None

    spatial_data_fields = ['southlimit', 'westlimit', 'northlimit', 'eastlimit', ]
    # todo lat lon
    for field in spatial_data_fields:
        if field not in data:
            print(2)
            return None

    box = '%f %f %f %f' % (
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
        # "filename": data['identifier'],
        # "@id": data['id'],
        "@type": "PropertyValue",  # todo 了解property value
        # "url": data['url'],
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
                "email": "nxgeilfus@gmail.com",
                "name": "Test Creator Name",
                "url": "https://www.hydroshare.org/user/10458/"
            }
        ]
    }
