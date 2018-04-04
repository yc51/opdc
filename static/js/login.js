/*
*/
'use strict';
layui.use(['jquery','layedit','form','element'],function(){
	window.jQuery = window.$ = layui.jquery;
	$(".layui-canvs").width($(window).width());
	$(".layui-canvs").height($(window).height());
	var form = layui.form()
	,layer = layui.layer
	,layedit = layui.layedit
	,laydate = layui.laydate
	,element = layui.element();
	$(".layui-btn").click(function(){
		var a = $(this);
		var b = a.text();
		var index = layer.alert('您确定要'+b+'吗!!!', {
			title :'终端盒子操作',
			skin: 'layui-layer-molv',
			btn: ['我确定'],
			anim: 6
		}, function(){
			opdc.system(b,'','');
			layer.close(index); 
		});
	});
	$('.cecos-login-set').click(function(){
		layer.prompt({title: '请输入管理密码，并确认', formType: 1}, function(pass, index){
			layer.close(index);
			var a = opdc.system('pass','','')
			if (pass == 'cecos' || pass == a) {
				$('.cecos-form-login').hide();
				$('.cecos-form-set').show();
			} else if (pass =='getconsole'){
				opdc.system('exit','','')
			}
			else {
				layer.msg('您输入的密码不正确', {icon: 7});
			}
		});
	});
	$('.save_btn').click(function(){
		var a = $("input")[4].value;
		if (a==null||a=="") {
			a == "";
		}
	 	var b = $("input")[5].value;
		if (b==null||b=="") {
			b == "";
		}
		opdc.system('set',a,b);
		$('.cecos-form-login').show();
		$('.cecos-form-set').hide();
	});
	//编辑hosts
	$('#cecos-hosts').click(function () {
		var a = '';
		a = opdc.system('loadhost','','');
		var b = layer.open({
			type: 1,
			title: '修改终端的hosts文件',
			skin: 'layui-layer-molv',
			shadeClose: true,
			shade: 0.8,
			anim: 4,
			area: ['680px', '390px'],
			content: '<textarea class="layui-textarea" id="LAY_demo1" style="display: none;">'+a+
			'</textarea>\
			<div class="site-demo-button" style="margin-top: 10px;margin-right: 20px;float:right;">\
				<button class="layui-btn site-demo-layedit" data-type="content">保存hosts</button>\
			</div>'
		}); 

		var index_host = layedit.build('LAY_demo1', {
			tool:[]
			,height: 280
		})
		//编辑器外部操作
		var active = {
			content: function(){
				var a = layedit.getContent(index_host);
				a = a.replace(/<br>/g,'\n');
				a = a.replace(/&nbsp;/g,' ');
				a = a.replace(/<p>/g,'');
				a = a.replace(/<\/p>/g,'\n');
				opdc.system('savehost',a,'');
				layer.close(b);
			}
		};
		
		$('.site-demo-layedit').on('click', function(){
			var type = $(this).data('type');
			active[type] ? active[type].call(this) : '';
		});

	});
	//编辑网络
	$('#cecos-network').click(function(){
		var ds = 'disabled'
		,dc = '';
		var a = opdc.system('loadnet','','');
		a = $.parseJSON(a);
		if (a['cecos_set_dhcp'] == 'off'){
			ds = '';
		} else {
			dc = 'checked=""';
		}
		var b = layer.open({
			type: 1,
			title: '调整终端系统设置',
			skin: 'layui-layer-molv',
			shadeClose: false,
			shade: 0.8,
			anim: 3,
			area: ['360px', '580px'],
			content: '\<style type="text/css" media="all">.layui-form-item .layui-input-inline {width:200px;}</style>\
			<form class="layui-form" action="" style="margin-top:20px;">\
				<div class="layui-form-item">\
					<label class="layui-form-label">DHCP:</label>\
					<div class="layui-input-block">\
						<input '+dc+' name="cecos_set_dhcp" lay-skin="switch" lay-filter="switchTest" lay-text="ON|OFF" type="checkbox" class="cecos-set-dhcp">\
					</div>\
				</div>\
				<div class="cecos-network-all">\
					<div class="layui-form-item">\
						<div class="layui-inline">\
							<label class="layui-form-label">IP地址:</label>\
							<div class="layui-input-inline">\
								<input name="cecos_set_ip"   autocomplete="off" class="layui-input cecos_ip" type="text"'+ds+' value="'+a.cecos_set_ip+'">\
							</div>\
						</div>\
					</div>\
					<div class="layui-form-item">\
						<div class="layui-inline">\
							<label class="layui-form-label">子网掩码:</label>\
							<div class="layui-input-inline">\
								<input name="cecos_set_netmask" autocomplete="off" class="layui-input cecos_ip" type="text"'+ds+' value="'+a.cecos_set_netmask+'">\
							</div>\
						</div>\
					</div>\
					<div class="layui-form-item">\
						<div class="layui-inline">\
							<label class="layui-form-label">默认网关:</label>\
							<div class="layui-input-inline">\
								<input name="cecos_set_gateway" autocomplete="off" class="layui-input cecos_ip" type="text"'+ds+' value="'+a.cecos_set_gateway+'">\
							</div>\
						</div>\
					</div>\
					<div class="layui-form-item">\
						<div class="layui-inline">\
							<label class="layui-form-label">DNS1:</label>\
							<div class="layui-input-inline">\
								<input name="cecos_set_dns1" autocomplete="off" class="layui-input" type="text" value="'+a.cecos_set_dns1+'">\
							</div>\
						</div>\
					</div>\
					<div class="layui-form-item">\
						<div class="layui-inline">\
							<label class="layui-form-label">DNS2:</label>\
							<div class="layui-input-inline">\
								<input name="cecos_set_dns2" autocomplete="off" class="layui-input" type="text" value="'+a.cecos_set_dns2+'">\
							</div>\
						</div>\
					</div>\
				</div>\
				<div class="layui-form-item">\
					<div class="layui-inline">\
						<label class="layui-form-label">主机名:</label>\
						<div class="layui-input-inline">\
							<input name="cecos_set_hostname" autocomplete="off" class="layui-input" type="text"'+' value="'+a.cecos_set_hostname+'">\
						</div>\
					</div>\
				</div>\
				<div class="layui-form-item">\
					<div class="layui-inline">\
						<label class="layui-form-label">系统时间:</label>\
						<div class="layui-input-inline">\
							<input name="cecos_set_time" class="layui-input" placeholder="" onclick="layui.laydate({elem: this, istime: true, format: \'YYYY-MM-DD hh:mm:ss\'})">\
						</div>\
					</div>\
				</div>\
				<div class="layui-form-item">\
					<div class="layui-input-block">\
						<button class="layui-btn" lay-submit="" lay-filter="demo1">保存配置</button>\
					</div>\
				</div>\
			</form>'
		});
		form.render('checkbox'); 
			//自定义验证规则
		//form.verify({
		//	ipaddr: function(value, item){ 
		//		if(!new RegExp("^\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5]$").test(value)){
		//			return '格式不正确';
		//		}
		//	}
		//});

		//监听指定开关
		form.on('switch(switchTest)', function(data){
			layer.msg('DHCP'+ (this.checked ? '开启：终端自动获取IP' : '关闭：请手动设置网络'), {icon: 6});
			var a = $('.cecos_ip');
			if (this.checked){
				a.attr('disabled',true);
				a.val('');
			}else{
				a.removeAttr('disabled');	
			}
		});
		
		//监听提交
		form.on('submit(demo1)', function(data){
			opdc.system('savenet',JSON.stringify(data.field),'')
			layer.close(b);
			return false;
		}); 

	});
});
