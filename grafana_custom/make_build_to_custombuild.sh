

find /opt/gamification/grafana_custom/build/ -name *.js -exec sed -i 's|"AppTitle","Grafana")|"AppTitle","MM.SUP Геймификация")|g' {} \;

find /opt/gamification/grafana_custom/build/ -name *.js -exec sed -i 's|AppTitle="Grafana"|AppTitle="MM.SUP Геймификация"|g' {} \;


find /opt/gamification/grafana_custom/build/ -name *.js -exec sed -i 's|LoginTitle="Welcome to Grafana"|LoginTitle="Welcome to Gamification"|g' {} \;

find /opt/gamification/grafana_custom/build/ -name *.js -exec sed -i 's|"LoginTitle","Welcome to Grafana")|"LoginTitle","Welcome to Gamification")|g' {} \;





find /opt/gamification/grafana_custom/build/ -name *.js -exec sed -i 's|.push({target:"_blank",id:"version",text:`${..edition}${.}`,url:..licenseUrl,icon:"external-link-alt"})||g' {} \;


find /opt/gamification/grafana_custom/build/ -name *.js -exec sed -i 's|..createElement(....,{className:.,onClick:.,iconOnly:!0,icon:"rss","aria-label":"News"})|null|g' {} \;


find /opt/gamification/grafana_custom/build/ -name *.js -exec sed -i 's|({target:"_blank",id:"updateVersion",.*grafana_footer"})|()|g' {} \;


find /opt/gamification/grafana_custom/build/ -name *.js -exec sed -i 's|({target:"_blank",id:"version",.*CHANGELOG.md":void 0})|()|g' {} \;


find /opt/gamification/grafana_custom/build/ -name *.js -exec sed -i 's|({target:"_blank",id:"license",.*licenseUrl})|()|g' {} \;


find /opt/gamification/grafana_custom/build/ -name *.js -exec sed -i 's|\[{target:"_blank",id:"documentation".*grafana_footer"}\]|\[\]|g' {} \;



find /opt/gamification/grafana_custom/build/ -name *.js -exec sed -i 's|{target:"_blank",id:"documentation",text:(0,r.t)("nav.help/documentation","Documentation"),icon:"document-info",url:"https://grafana.com/docs/grafana/latest/?utm_source=grafana_footer"},{target:"_blank",id:"support",text:(0,r.t)("nav.help/support","Support"),icon:"question-circle",url:"https://grafana.com/products/enterprise/?utm_source=grafana_footer"},{target:"_blank",id:"community",text:(0,r.t)("nav.help/community","Community"),icon:"comments-alt",url:"https://community.grafana.com/?utm_source=grafana_footer"}||g' {} \;

 find /opt/gamification/grafana_custom/build/ -name *.js -exec sed -i 's|{target:"_blank",id:"version",text:`${e.edition}${s}`,url:t.licenseUrl}||g' {} \;

find /opt/gamification/grafana_custom/build/ -name *.js -exec sed -i 's|{target:"_blank",id:"version",text:`v${e.version} (${e.commit})`,url:i?"https://github.com/grafana/grafana/blob/main/CHANGELOG.md":void 0}||g' {} \;

find /opt/gamification/grafana_custom/build/ -name *.js -exec sed -i 's|{target:"_blank",id:"updateVersion",text:"New version available!",icon:"download-alt",url:"https://grafana.com/grafana/download?utm_source=grafana_footer"}||g' {} \;





