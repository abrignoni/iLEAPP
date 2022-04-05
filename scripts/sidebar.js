/*-------------Custom Javascript---------------*/

var btnst = false;
function sidebar_toggle() {
  if(btnst == true) {
      /*--Styles with sidebar visible--*/
      document.getElementById("sidebar_id").style.width = "16.666667%"; /*--#sidebar_id width--*/
      document.getElementById("sidebar_id").style.transition = "0.5s"; /*--transition duration for #sidebar_id--*/
      
      document.getElementById("main").style.marginLeft = "16.666667%"; /*--#main margin--*/
      document.getElementById("main").style.maxWidth = "83.333333%"; /*--max width of #main--*/
      document.getElementById("main").style.transition = "0.5s";  /*--transition duration for #main--*/
      
    btnst = false;
  }else if(btnst == false) {
    /*--Styles with sidebar hidden--*/  
    document.getElementById("main").style.marginLeft = "0"; /*--#main margin--*/
    document.getElementById("main").style.maxWidth = "100%"; /*--max width of #main--*/
    document.getElementById("main").style.transition = "0.5s"; /*--transition duration for #main--*/
      
    document.getElementById("sidebar_id").style.width = "0"; /*--#sidebar_id width--*/
    document.getElementById("sidebar_id").style.transition = "0.5s"; /*--transition duration for #sidebar_id--*/
    btnst = true;
  }
}

