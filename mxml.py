from lxml import etree
import datetime

# - AuditTrailEntry
#   - WorkflowModelElement
#   - EventType (e.g. assign, complete)
#   - Timestamp (e.g. 2005-02-07T15:30:00.000+00:00)
def parse_AuditTrailEntry(element):
    entry = dict()
    for item in element:
        if item.tag == 'WorkflowModelElement':
            entry['name'] = item.text.strip()
        elif item.tag == 'EventType':
            entry['type'] = item.text.strip()
        elif item.tag == 'Timestamp':
            entry['timestamp'] = item.text.strip()
    return entry


def parse(filepath):
    tree = etree.parse(filepath)
    root = tree.getroot()

    # - process
    #   - ProcessInstance(*)
    #       - AuditTrailEntry(*)
    process = root.xpath('./Process')[0]
    traces = []
    instance_id_list = []
    events = set()
    for instance in process:
        trace = []
        for item in instance:
            if item.tag == 'AuditTrailEntry':
                entry = parse_AuditTrailEntry(item)
                if entry['type'] == 'assign':
                    trace.append(entry['name'])
                    events.add(entry['name'])
                    # print entry['timestamp'],
        # print
        traces.append(trace)
        instance_id_list.append(instance.get('id'))
    return {
        'traces': traces,
        'instance_id_list': instance_id_list,
        'events': events
    }


def write(traces, filepath):
    timestamp = datetime.datetime.now()
    timestep = datetime.timedelta(minutes=1)  # increase timestamp by 1 minute per event
    root = etree.parse('template.mxml', parser=etree.XMLParser(remove_blank_text=True))
    process = root.xpath('.//Process')[0]

    # important for pretty_print option in serialization
    # if process.text or process.tail is not None, extra indent and new line will not be added
    process.text = None

    for index, trace in enumerate(traces):
        instance = etree.SubElement(process, 'ProcessInstance', {'id': str(index)})
        for event in trace:
            entry = etree.SubElement(instance, 'AuditTrailEntry')
            etree.SubElement(entry, 'WorkflowModelElement').text = event
            etree.SubElement(entry, 'EventType').text = 'assign'
            etree.SubElement(entry, 'Timestamp').text = timestamp.isoformat()
            timestamp += timestep

            entry = etree.SubElement(instance, 'AuditTrailEntry')
            etree.SubElement(entry, 'WorkflowModelElement').text = event
            etree.SubElement(entry, 'EventType').text = 'complete'
            etree.SubElement(entry, 'Timestamp').text = timestamp.isoformat()
            timestamp += timestep

    root.write(filepath, encoding='utf-8', method="xml", pretty_print=True)

if __name__ == '__main__':
    filepath = r'E:\BPM\QUT 2016 - Fast and Accurate Business Process Drift Detection\Logs\LoanAssessment_LOGS\logs\cb\cb2.5k.mxml'
    log = parse(filepath)
    for trace in log[:10]:
        print trace
