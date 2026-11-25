// Pixel, la mascota voxel de InnovaSites. sprite(o) -> matriz; svg(o, px) -> SVG voxel.
const PW=27,PH=32,PAL={O:'#1d0503',R:'#E5342A',r:'#a8211a',H:'#ff7468',K:'#0a0b10',k:'#15171f',W:'#ffffff',E:'#ff4a3d',G:'#c9ced8',Y:'#ffd34d',S:'#5a120d',V:'#34c759'};
function sprite(o){
  const g=[...Array(PH)].map(()=>Array(PW).fill('.'));
  const P=(x,y,c)=>{if(x>=0&&x<PW&&y>=0&&y<PH)g[y][x]=c};
  const rect=(x0,y0,x1,y1,c)=>{for(let y=y0;y<=y1;y++)for(let x=x0;x<=x1;x++)P(x,y,c)};
  const ox=2;
  // antena con luz
  rect(11+ox,1,12+ox,3,'G'); rect(10+ox,0,13+ox,0,'Y'); rect(11+ox,-1,12+ox,0,'Y');
  // cabeza (monitor)
  rect(2+ox,4,21+ox,20,'O'); rect(3+ox,5,20+ox,19,'R');
  [[2,4],[21,4],[2,20],[21,20]].forEach(([x,y])=>P(x+ox,y,'.'));[[3,5],[20,5],[3,19],[20,19]].forEach(([x,y])=>P(x+ox,y,'O'));
  rect(4+ox,6,10+ox,6,'H'); P(4+ox,7,'H'); P(4+ox,8,'H');
  rect(4+ox,18,20+ox,19,'r'); rect(20+ox,6,20+ox,19,'r');
  // pantalla de la cara
  rect(5+ox,7,18+ox,17,'O'); rect(6+ox,8,17+ox,16,'K');
  for(let x=6;x<=17;x++)for(let y=8;y<=16;y++)if((x*3+y*5)%7==0)P(x+ox,y,'k');
  // ---------- cara (pantalla LED) ----------
  const pat=(rows,x0,y0,c,flip)=>rows.forEach((r,j)=>[...r].forEach((ch,i)=>{ if(ch!=='.'){ const xx=flip? x0+r.length-1-i : x0+i; P(xx+ox,y0+j, ch==='#'?c:ch);} }));
  const dx=o.dx||0, dy=o.dy||0;
  const ICON={
    lock:['....WWWW....','...W....W...','...W....W...','..RRRRRRRR..','..RRRKKRRR..','..RRRKKRRR..','..RRRRRRRR..'],
    warn:['.....YY.....','....YKKY....','....YKKY....','...YYKKYY...','...YYYYYY...','..YYYKKYYY..','..YYYYYYYY..'],
    check:['..........VV','.........VV.','VV......VV..','.VV....VV...','..VV..VV....','...VVVV.....','....VV......'],
    q:['....WWWW....','...W....W...','........W...','......WW....','.....W......','............','.....W......'],
  };
  if(o.icon && ICON[o.icon]) { pat(ICON[o.icon],6,9,'W'); }
  else {
    const L=(rows,c)=>pat(rows,6+dx,8+dy,c,false), R=(rows,c)=>pat(rows,13+dx,8+dy,c,false);
    const E=o.eyes||'open';
    if(E==='open'){ const lt=[[9,8],[8,9],[7,10],[8,11],[9,12]], gt=[[14,8],[15,9],[16,10],[15,11],[14,12]];
      lt.forEach(([x,y])=>{P(x+ox+dx,y+dy,'E');P(x+1+ox+dx,y+dy,'E')}); gt.forEach(([x,y])=>{P(x+ox+dx,y+dy,'W');P(x-1+ox+dx,y+dy,'W')}); }
    else if(E==='blink'){ rect(7+ox,10,10+ox,10,'E'); rect(13+ox,10,16+ox,10,'W'); }
    else if(E==='wide'){ rect(7+ox+dx,8+dy,10+ox+dx,11+dy,'W'); rect(8+ox+dx,9+dy,9+ox+dx,10+dy,'K'); rect(13+ox+dx,8+dy,16+ox+dx,11+dy,'W'); rect(14+ox+dx,9+dy,15+ox+dx,10+dy,'K'); }
    else if(E==='wink'){ const lt=[[9,8],[8,9],[7,10],[8,11],[9,12]]; lt.forEach(([x,y])=>{P(x+ox,y,'E');P(x+1+ox,y,'E')}); [[13,11],[14,10],[15,10],[16,11]].forEach(([x,y])=>P(x+ox,y,'W')); }
    else if(E==='happy'){ L(['.....','.##..','#..#.','.....'],'E'); R(['.....','.##..','#..#.','.....'],'W'); }
    else if(E==='angry'){ L(['#....','.##..','..##.','.###.','.....'],'E'); R(['....#','..##.','.##..','.###.','.....'],'W'); }
    else if(E==='sad'){ L(['...#.','..#..','.##..','.##..'],'E'); R(['#....','.#...','.##..','.##..'],'W'); }
    else if(E==='sus'){ L(['.....','.....','####.','.##..'],'E'); R(['.....','.....','####.','.##..'],'W'); }
    else if(E==='heart'){ L(['.#.#.','#####','#####','.###.','..#..'],'E'); R(['.#.#.','#####','#####','.###.','..#..'],'E'); }
    else if(E==='x'){ L(['#..#.','.##..','.##..','#..#.'],'E'); R(['#..#.','.##..','.##..','#..#.'],'E'); }
    else if(E==='star'){ L(['.#...','###..','.#...'],'Y'); R(['.#...','###..','.#...'],'Y'); }
    else if(E==='think'){ pat(['..##','..##','....'],7,8,'E'); pat(['..##','..##','....'],13,8,'W'); P(17+ox,13,'W'); P(16+ox,13,'W'); }
    // boca
    const Mo=o.mouth||'smile', m=(rows,c,y=14)=>pat(rows,9,y,c);
    if(Mo==='mid'){ rect(10+ox,14,13+ox,14,'E'); rect(11+ox,15,12+ox,15,'E'); }
    else if(Mo==='talk'){ rect(10+ox,14,13+ox,15,'E'); rect(11+ox,15,12+ox,15,'H'); }
    else if(Mo==='o'){ rect(11+ox,14,12+ox,15,'W'); }
    else if(Mo==='wide'){ m(['.####.','#HHHH#','.####.'],'E',13); }
    else if(Mo==='flat'){ m(['......','.####.'],'W'); }
    else if(Mo==='frown'){ m(['.####.','#....#'],'W'); }
    else if(Mo==='smirk'){ m(['....#.','.###..'],'W'); }
    else if(Mo==='grin'){ m(['######','#EEEE#'],'W'); }
    else if(Mo==='zig'){ m(['.#..#.','#.##.#'],'W'); }
    else if(Mo==='ee'){ m(['######','.EEEE.'],'E'); }
    else { [[9,14],[14,14],[10,15],[11,15],[12,15],[13,15]].forEach(([x,y])=>P(x+ox,y,'W')); }
  }
  // cuerpo
  rect(10+ox,21,13+ox,21,'S');
  rect(6+ox,22,17+ox,27,'O'); rect(7+ox,22,16+ox,26,'R'); rect(7+ox,26,16+ox,26,'r'); rect(7+ox,22,9+ox,22,'H');
  [[13,23],[12,24],[11,25]].forEach(([x,y])=>{P(x+ox,y,'S');P(x+1+ox,y,'S')});
  // brazo izquierdo
  rect(3+ox,22,5+ox,23,'r'); rect(3+ox,24,4+ox,25,'r'); P(4+ox,23,'R'); P(3+ox,25,'W');P(4+ox,25,'W');
  if(o.arm==='point'||o.arm==='wave'){ const pts=o.arm==='point'?[[18,22],[19,21],[20,20],[21,19],[22,18]]:[[18,22],[19,21],[19,20],[20,19],[20,18]];
    pts.forEach(([x,y])=>{P(x+ox,y,'R');P(x+ox,y+1,'r')}); pts.slice(1,-1).forEach(([x,y])=>P(x+ox,y,'R')); const [hx,hy]=pts[pts.length-1]; rect(hx+ox,hy-2,hx+1+ox,hy-1,'W'); }
  else { rect(18+ox,22,20+ox,23,'r'); rect(19+ox,24,20+ox,25,'r'); P(19+ox,23,'R'); P(19+ox,25,'W');P(20+ox,25,'W'); }
  // piernas
  rect(8+ox,28,10+ox,29,'r'); rect(13+ox,28,15+ox,29,'r'); rect(8+ox,30,11+ox,30,'S'); rect(13+ox,30,16+ox,30,'S');
  if(o.excl){ rect(22+ox,0,23+ox,3,'Y'); rect(22+ox,5,23+ox,5,'Y'); }
  return g;
}
function shade(hex,k){const n=parseInt(hex.slice(1),16);let r=n>>16,g=n>>8&255,b=n&255;const f=c=>Math.max(0,Math.min(255,Math.round(k>0?c+(255-c)*k:c*(1+k))));return `rgb(${f(r)},${f(g)},${f(b)})`;}
function pixelSVG(o,px=11.5){
  const g=sprite(o), D=px*.55; let sides='', fronts='', glow='';
  const has=(x,y)=>y>=0&&y<PH&&x>=0&&x<PW&&g[y][x]!=='.'&&g[y][x]!=='O';
  g.forEach((row,y)=>row.forEach((c,x)=>{ if(c==='.'||c==='O')return; const col=PAL[c], X=x*px, Y=y*px;
    if(!has(x,y-1)) sides+=`<path d="M${X} ${Y} L${X+D} ${Y-D} L${X+px+D} ${Y-D} L${X+px} ${Y} Z" fill="${shade(col,.28)}"/>`;
    if(!has(x+1,y)) sides+=`<path d="M${X+px} ${Y} L${X+px+D} ${Y-D} L${X+px+D} ${Y+px-D} L${X+px} ${Y+px} Z" fill="${shade(col,-.42)}"/>`;
    const lit = .10 - (y/PH)*.22 - (x/PW)*.08;
    const emis = (c==='E'||c==='V'||c==='Y'||(c==='W'||c==='R'||c==='H')&&y>=8&&y<=16&&x>=8&&x<=19);
    fronts+=`<rect x="${X}" y="${Y}" width="${px+.4}" height="${px+.4}" fill="${emis?col:shade(col,lit)}"/>`;
    if(!emis && c!=='K' && c!=='k') fronts+=`<rect x="${X+1}" y="${Y+1}" width="${px*.38}" height="${px*.16}" fill="rgba(255,255,255,.10)"/>`;
    if(emis) glow+=`<rect x="${X-2}" y="${Y-2}" width="${px+4}" height="${px+4}" rx="3" fill="${col}" opacity=".9"/>`;
  }));
  const cubes=[[0,6,1],[24.5,2,.8],[25,13,.6],[-.5,21,.7],[23.5,26,.9]].map(([x,y,s],i)=>{const S=px*s,X=x*px,Y=y*px,d=S*.55,c=i%2?'#E5342A':'#ffffff';
    return `<g opacity="${.55+.1*i}"><path d="M${X} ${Y} L${X+d} ${Y-d} L${X+S+d} ${Y-d} L${X+S} ${Y} Z" fill="${shade(c,.3)}"/><path d="M${X+S} ${Y} L${X+S+d} ${Y-d} L${X+S+d} ${Y+S-d} L${X+S} ${Y+S} Z" fill="${shade(c,-.45)}"/><rect x="${X}" y="${Y}" width="${S}" height="${S}" fill="${c}"/></g>`}).join('');
  return `<svg width="${(PW+2)*px}" height="${(PH+2)*px}" viewBox="${-px} ${-px*1.5} ${(PW+2)*px} ${(PH+2)*px}" shape-rendering="crispEdges">
   <defs><filter id="pxbl" x="-.5" y="-.5" width="2" height="2"><feGaussianBlur stdDeviation="7"/></filter>
   <radialGradient id="pxhalo"><stop offset="0" stop-color="rgba(229,52,42,.45)"/><stop offset="1" stop-color="rgba(229,52,42,0)"/></radialGradient></defs>
   <ellipse cx="${PW*px/2}" cy="${PH*px*.45}" rx="${PW*px*.62}" ry="${PH*px*.55}" fill="url(#pxhalo)"/>
   <ellipse cx="${PW*px/2}" cy="${(PH-.2)*px}" rx="${PW*px*.3}" ry="${px*.9}" fill="rgba(229,52,42,.45)" filter="url(#pxbl)"/>
   ${cubes}${sides}${fronts}<g filter="url(#pxbl)" style="mix-blend-mode:screen">${glow}</g></svg>`;
}


// ---------- Pixel por partes (cabeza, cuerpo, brazos, piernas) para animarlo libre ----------
// Cada parte es una región de la matriz; se dibuja como voxel sin halo ni piso.
function voxPart(g, px, x0, y0, x1, y1, uid) {
  const D = px * .55; let sides = '', fronts = '', glow = '';
  const has = (x, y) => y >= y0 && y <= y1 && x >= x0 && x <= x1 && g[y] && g[y][x] && g[y][x] !== '.' && g[y][x] !== 'O';
  for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) {
    const c = g[y] && g[y][x]; if (!c || c === '.' || c === 'O') continue;
    const col = PAL[c], X = (x - x0) * px, Y = (y - y0) * px;
    if (!has(x, y - 1)) sides += `<path d="M${X} ${Y} L${X + D} ${Y - D} L${X + px + D} ${Y - D} L${X + px} ${Y} Z" fill="${shade(col, .28)}"/>`;
    if (!has(x + 1, y)) sides += `<path d="M${X + px} ${Y} L${X + px + D} ${Y - D} L${X + px + D} ${Y + px - D} L${X + px} ${Y + px} Z" fill="${shade(col, -.42)}"/>`;
    const lit = .10 - (y / PH) * .22 - (x / PW) * .08;
    const emis = (c === 'E' || c === 'V' || c === 'Y' || (c === 'W' || c === 'R' || c === 'H') && y >= 8 && y <= 16 && x >= 8 && x <= 19);
    fronts += `<rect x="${X}" y="${Y}" width="${px + .4}" height="${px + .4}" fill="${emis ? col : shade(col, lit)}"/>`;
    if (!emis && c !== 'K' && c !== 'k') fronts += `<rect x="${X + 1}" y="${Y + 1}" width="${px * .38}" height="${px * .16}" fill="rgba(255,255,255,.10)"/>`;
    if (emis) glow += `<rect x="${X - 2}" y="${Y - 2}" width="${px + 4}" height="${px + 4}" rx="3" fill="${col}" opacity=".9"/>`;
  }
  const w = (x1 - x0 + 1) * px, h = (y1 - y0 + 1) * px, m = px * 1.2;
  return `<svg width="${w + 2 * m}" height="${h + 2 * m}" viewBox="${-m} ${-m} ${w + 2 * m} ${h + 2 * m}" shape-rendering="crispEdges" style="position:absolute;left:${-m}px;top:${-m}px;overflow:visible">
   <defs><filter id="gl${uid}" x="-.5" y="-.5" width="2" height="2"><feGaussianBlur stdDeviation="6"/></filter></defs>
   ${sides}${fronts}${glow ? `<g filter="url(#gl${uid})" style="mix-blend-mode:screen">${glow}</g>` : ''}</svg>`;
}
// regiones (con ox=2 ya aplicado): cabeza 4..23 x -1..20, cuerpo 8..19 x 21..27
function pixelHead(o, px) { const g = sprite(Object.assign({}, o, { arm: 'none' })); return voxPart(g, px, 4, 0, 24, 20, 'h'); }
function pixelBody(px) { const g = sprite({ arm: 'none' }); for (let y = 22; y <= 25; y++) for (const x of [5, 6, 7, 20, 21, 22]) g[y][x] = '.'; return voxPart(g, px, 8, 21, 19, 27, 'b'); }
function pixelLimb(kind, px) {   // brazo: 3x8 con mano blanca; pierna: 3x4
  const g = kind === 'arm' ? ['RRR', 'RRr', 'RRr', 'RRr', 'RRr', 'rrr', 'WWW', 'WWW'] : ['rrr', 'rrr', 'rrr', 'SSSS'];
  return voxPart(g.map(r => r.split('')), px, 0, 0, 3, g.length - 1, kind);
}
