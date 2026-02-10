#!/bin/bash
# Scrape NASDAQ 100 top 5 gainers/losers from slickcharts
cd "$(dirname "$0")"

node -e "
const https = require('https');
const fetch = url => new Promise((res,rej) => {
  https.get(url, {headers:{'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}}, r => {
    let d=''; r.on('data',c=>d+=c); r.on('end',()=>res(d));
  }).on('error',rej);
});

(async()=>{
  const parse = html => {
    const rows = [];
    // Each row: <td>...<a>Company</a></td><td><a>SYMBOL</a></td><td>price</td><td style=color:green/red>chg</td><td>(pct%)</td>
    const re = /<tr><td[^>]*><a[^>]*>([^<]+)<\/a><\/td><td><a[^>]*>([^<]+)<\/a><\/td><td[^>]*>.*?([\d,.]+)<\/td><td[^>]*>([-\d,.]+)<\/td><td[^>]*>\(([-\d,.]+%)\)<\/td><\/tr>/g;
    let m;
    while ((m = re.exec(html)) && rows.length < 5) {
      rows.push({
        company: m[1].trim(),
        symbol: m[2].trim(),
        price: parseFloat(m[3].replace(/,/g,'')),
        change: parseFloat(m[4].replace(/,/g,'')),
        pctChange: m[5]
      });
    }
    return rows;
  };

  try {
    const [gHtml, lHtml] = await Promise.all([
      fetch('https://www.slickcharts.com/nasdaq100/gainers'),
      fetch('https://www.slickcharts.com/nasdaq100/losers')
    ]);
    const gainers = parse(gHtml);
    const losers = parse(lHtml);
    const out = { gainers, losers, lastUpdated: Date.now(), source: 'slickcharts.com' };
    require('fs').writeFileSync('market-movers.json', JSON.stringify(out, null, 2));
    console.log('OK: ' + gainers.length + ' gainers, ' + losers.length + ' losers');
  } catch(e) { console.error(e.message); }
})();
"
