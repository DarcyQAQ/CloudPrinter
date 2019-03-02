<template>
	<div>
		<el-form ref='form' :model="form" :rules="form_rules" label-width="80px">
			<el-form-item label="名称" prop="name">
				<el-input v-model="form.name"></el-input>
			</el-form-item>
			<el-form-item label="位置" prop="location">
				<el-input v-model="form.location"></el-input>
			</el-form-item>
			<el-row>
			    <el-col :offset="12" :span="12">			     
			        <el-button type="primary" round @click="add_printers">提交</el-button>
			    </el-col>
			</el-row>
		</el-form>
	</div>
</template>

<script>
	import 'whatwg-fetch';
	export default {
		data() {
			return {
				form: {
				    name: '',
					location: '',
				},
				form_rules:{
				    printer_name:[
				        {required: true, message: '请输入打印机名称', trigger: 'blur'}
				    ]
				}
			};
		},
		methods:{
			add_printers: function(){
				const vm = this
// 				if(this.form.token === ''){
// 				    vm.$message({
// 				        type: 'warning',
// 				        message: '请上传文件或等待文件上传完成！'
// 				    })
// 				    return
// 				}
				vm.$refs.form.validate(valid => {
				    if(valid){
				        fetch('http://127.0.0.1:8888/api/add_printers', {
				            method: 'POST',
				            body: JSON.stringify(vm.form)
				        }).then(response => {
				            return response.json()
				        }).then(response => {
				            if(response.status === 'success'){
				                vm.$message({
				                    type: 'success',
				                    message: '打印成功'
				                })
				                vm.reset_form()
				            }else{
				                vm.$message({
				                    type: 'error',
				                    message: 'error:' + response.message
				                })
				            }
				        })
				    }
				})
			}
		}
	}
</script>
