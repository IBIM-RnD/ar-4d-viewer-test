// 마커 인식을 화면 그리기와 분리해서 돌린다. 화면이 인식 속도에 묶이지 않게 하기 위함.
importScripts('vendor/cv.js', 'vendor/aruco.js');
const detector = new AR.Detector({dictionaryName: 'ARUCO_MIP_36h12'});
let cv = null, ctx = null;
onmessage = e => {
  const {bitmap, w, h, t} = e.data;
  try {
    if (!cv || cv.width !== w || cv.height !== h) { cv = new OffscreenCanvas(w, h); ctx = cv.getContext('2d', {willReadFrequently: true}); }
    const t0 = performance.now();
    ctx.drawImage(bitmap, 0, 0, w, h); bitmap.close();
    const ms = detector.detect(ctx.getImageData(0, 0, w, h)).map(m => ({id: m.id, corners: m.corners.map(p => ({x: p.x, y: p.y}))}));
    postMessage({markers: ms, ms: performance.now() - t0, w, h, t});
  } catch (err) { postMessage({markers: [], ms: 0, w, h, t, error: String(err)}); }
};
