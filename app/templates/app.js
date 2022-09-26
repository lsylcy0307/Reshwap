// $(document).ready(function() {

//     $('.updateButton').on('click', function(){
//         var list_type = $(this).attr('list_type');

//         req = $.ajax({
//             url: '/update',
//             type: 'POST',
//             data: {list_type: list_type}
//         });

//         req.done(function(data) {
//             // $scope.items = data.items
//             // document.getElementById("items_table").innerHTML=
//         });
//     });
// });


let menu = document.querySelector('#menu-icon');
let navbar = document.querySelector('.navbar');

menu.onclick = () => {
	menu.classList.toggle('bx-x');
	navbar.classList.toggle('active');
};

window.onscroll = () => {
	menu.classList.remove('bx-x');
	navbar.classList.remove('active');
};