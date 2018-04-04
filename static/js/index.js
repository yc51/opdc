'use strict';
layui.use(['jquery','layer','element','form'],function(){
	window.jQuery = window.$ = layui.jquery;
	window.layer = layui.layer;
	var element = layui.element();
	var form = layui.form();
  
// larry-side-menu向左折叠
$('.larry-side-menu').click(function() {
  var sideWidth = $('#larry-side').width();
  if(sideWidth === 130) {
      $('#larry-body').animate({
        left: '0'
      },"fast"); //admin-footer
      $('#larry-footer').animate({
        left: '0'
      },"fast");
      $('#larry-side').animate({
        width: '0'
      },"fast");
  } else {
      $('#larry-body').animate({
        left: '130px'
      },"fast");
      $('#larry-footer').animate({
        left: '130px'
      },"fast");
      $('#larry-side').animate({
        width: '130px'
      },"fast");
  }
});

//切换用户
$('.cecos-loginout').click(function() {
	opdc.changeuser();
});
//所有机器
$('#cecos-all').click(function(){
	$('.cecos-name').css('display','block');
});
$('#cecos-up').click(function(){
	$('.cecos-name').css('display','block');
	$('.cecos-name').filter('[status="down"]').css('display','none');
});
$('#cecos-down').click(function(){
	$('.cecos-name').css('display','none');
	$('.cecos-name').filter('[status="down"]').css('display','block');
});
//关机
$('#cecos-reboot').click(function () {
	var b='重启';
	var index = layer.alert('您确定要'+b+'吗!!!', {
		title :'终端盒子操作',
		skin: 'layui-layer-molv',
		btn: ['我确定'],
		anim: 2
	}, function(){
		opdc.system(b,'','');
		layer.close(index); 
	});
});
//
$('#cecos-shutdown').click(function () {
	var b='关机';
	var index = layer.alert('您确定要'+b+'吗!!!', {
		title :'终端盒子操作',
		skin: 'layui-layer-molv',
		btn: ['我确定'],
		anim: 1
	}, function(){
		if (($('fieldset').length == 1) && ($('#cecos-switch').prop('checked')==true)) {
			$('#larry-body').children('[status="up"]:first').find('button:eq(2)').click();
		} 
		opdc.system(b,'','');
		layer.close(index);
	});
});
$('#cecos-display').click(function(){
	var a = opdc.system('display','','');
	if (a == 'wmctrl'){
		layer.msg('请安装wmctrl', {icon: 7});
	}else if (a == 'lxrandr'){
		layer.msg('请安装lxrandr', {icon: 7});
	}
});
//联动开关
$("#cecos-switch").click(function(){
  var a = '0'
	if ($('#cecos-switch').prop('checked')==true) {
		a = '1';
	}
  opdc.vmswitch(a);
});


});