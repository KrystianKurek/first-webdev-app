import xml.etree.ElementTree as ET


def dict_to_xml(adict):
    root = ET.Element("trains")
    for key, value in adict.items():
        temp = {k: str(v) for k,v in value.items()}
        ET.SubElement(root, key, temp)
    return ET.tostring(root, encoding='utf8', method='xml')
