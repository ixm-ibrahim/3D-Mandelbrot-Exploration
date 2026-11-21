// Parameter sets for the text grid when the page is built with the new approaches (offsets and all).
window.VARIANTS = {
  mercator: [{ planes: 1 }, { planes: 2 }, { planes: 1, turn: 30 }, { planes: 2, turn: -45 }, { planes: 1, lift: 0.5 }, { planes: 4 }],
  lathe: [{ spin: 1 }, { spin: 3 }],
  bulb: [{}, { lon: 45 }, { lat: 20 }],
  classic: [{}, { phi: 45 }, { theta: 30 }],
  split: [{}],
};
return Object.keys(window.VARIANTS).join(' ');
