// JavaScript Document

 $(function ()
	   { 
	     $("ul li").click(function ()
		                                  { 
										    $(this).addClass('hover');//当前添加hover类
											$(this).siblings().removeClass('hover')//其他同级元素去掉hover类
										  }
										)
	   }
	 )
	 
	 
	 if (document.getElementById){
document.write('<style type="text/css">\n')
document.write('.submenu{display: none;}\n')
document.write('</style>\n')
}

function SwitchMenu(obj){
if(document.getElementById){
var el = document.getElementById(obj);
var ar = document.getElementById("masterdiv").getElementsByTagName("span"); 
	if(el.style.display != "block"){
		for (var i=0; i<ar.length; i++){
	if (ar[i].className=="submenu") //DynamicDrive.com change
			ar[i].style.display = "none";
		}
		el.style.display = "block";
	}else{
	el.style.display = "none";
	}
	}
}

function setTab(name,cursel){
	cursel_0=cursel;
	for(var i=1; i<=links_len; i++){
		var text_tj = document.getElementById(name+i);
		var text_show = document.getElementById("con_"+name+"_"+i);
		if(i==cursel){
			text_tj.className="off";
			text_show.style.display="block";
		}
		else{
			text_tj.className="";
			text_show.style.display="none";
		}
	}
}
function Next(){                                                        
	cursel_0++;
	if (cursel_0>links_len)cursel_0=1
	setTab(name_0,cursel_0);
} 
var name_0='one';
var cursel_0=1;
var ScrollTime=3000;//循环周期（毫秒）
var links_len,iIntervalId;
onload=function(){
	var links = document.getElementById("select").getElementsByTagName('li')
	links_len=links.length;
}



	 