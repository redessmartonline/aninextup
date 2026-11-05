#!/usr/bin/env python3
"""Fetch and validate GA4's last 30 complete days before changing Popular News."""
from datetime import datetime, timedelta
import json
import os
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from build_popular_news import ROOT, render, select

PROPERTY = '559369724'
HOSTS = ['aninextup.com', 'www.aninextup.com']
DIMENSIONS = ['hostName', 'pagePath']


def fetch_report(token):
    request = Request(
        f'https://analyticsdata.googleapis.com/v1beta/properties/{PROPERTY}:runReport',
        data=json.dumps({
            'dateRanges': [{'startDate': '30daysAgo', 'endDate': 'yesterday'}],
            'dimensions': [{'name': name} for name in DIMENSIONS],
            'metrics': [{'name': 'screenPageViews'}],
            'dimensionFilter': {'andGroup': {'expressions': [
                {'filter': {'fieldName': 'hostName', 'inListFilter': {'values': HOSTS}}},
                {'filter': {'fieldName': 'pagePath', 'stringFilter': {
                    'matchType': 'BEGINS_WITH', 'value': '/articles/'
                }}},
            ]}},
            'limit': '10000',
        }).encode(),
        headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'},
    )
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def snapshot_from_report(report, started, finished):
    metadata = report['metadata']
    zone = ZoneInfo(metadata['timeZone'])
    day = started.astimezone(zone).date()
    if day != finished.astimezone(zone).date():
        raise ValueError('Report crossed midnight in the GA4 property timezone')
    rows = report.get('rows', [])
    if len(rows) != report.get('rowCount', 0) or metadata.get('subjectToThresholding'):
        raise ValueError('Incomplete or thresholded GA4 report')
    if [item['name'] for item in report.get('dimensionHeaders', [])] != DIMENSIONS:
        raise ValueError('Unexpected GA4 dimensions')
    if [item['name'] for item in report.get('metricHeaders', [])] != ['screenPageViews']:
        raise ValueError('Unexpected GA4 metric')
    return {
        'source': 'GA4', 'property': PROPERTY, 'metric': 'screen_page_views',
        'dateFrom': (day - timedelta(days=30)).isoformat(),
        'dateTo': (day - timedelta(days=1)).isoformat(),
        'checkedAt': day.isoformat(),
        'propertyTimeZone': metadata['timeZone'],
        'totalRows': len(rows),
        'limitations': ['GA4 records measured page views, not all readership.'],
        'rows': [
            {
                'hostname': row['dimensionValues'][0]['value'],
                'page_path': row['dimensionValues'][1]['value'],
                'screen_page_views': int(row['metricValues'][0]['value']),
            }
            for row in rows
        ],
    }


def main():
    token = os.environ['GA4_ACCESS_TOKEN']
    started = datetime.now().astimezone()
    report = fetch_report(token)
    snapshot = snapshot_from_report(report, started, datetime.now().astimezone())
    target = ROOT / 'index.html'
    before = target.read_text(encoding='utf-8')
    ranked = select(snapshot, ROOT)
    after = render(before, snapshot, ranked)
    # Validate everything before replacing either file. Git publishes the pair together.
    (ROOT / 'assets/popular-news.json').write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )
    if after != before:
        target.write_text(after, encoding='utf-8')
    print(f'Popular News verified: {snapshot["dateFrom"]} through {snapshot["dateTo"]}')


if __name__ == '__main__':
    main()
