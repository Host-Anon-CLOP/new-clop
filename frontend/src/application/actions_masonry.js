import Masonry from 'masonry-layout';
// const grid = document.querySelector('.masonry');
//
// new Masonry( grid, {
//     percentPosition: true,
// });

const grids = document.getElementsByClassName("masonry");
for (let i = 0; i < grids.length; i++) {
    new Masonry( grids[i], {
        percentPosition: true,
    });
}