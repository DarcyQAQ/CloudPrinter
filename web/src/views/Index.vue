<template>
    <div>
        <el-upload ref="upload" drag action="http://127.0.0.1:8888/api/upload"
                   :multiple="false" name="file" :limit="1"
                   :on-success="upload_success"
                   :on-exceed="upload_exceed"
                   width="100%">
            <i class="el-icon-upload"></i>
            <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
            <div class="el-upload__tip" slot="tip">该打印服务不会保存用户的文件数据</div>
        </el-upload>
        <br />
        <!-- <el-card class="box-card" header="文件信息">
        </el-card>
        <br /> -->
        <el-form ref='form' :model="form" :rules="form_rules" label-width="80px">
            <el-form-item label="打印机" prop="printer">
                <el-select v-model="form.printer" placeholder="请选择">
                    <el-option v-for="item in printer_list" :key="item.name" :label="item.name" :value="item.name">
                        <span style="float: left">{{ item.name }}</span>
                        <span style="float: right; color: #8492a6; font-size: 13px">{{ item.position }}</span>
                    </el-option>
                </el-select>
            </el-form-item>
            <el-form-item label="份数" prop="copies">
                <el-input-number v-model="form.copies" :min="1" :max="20"></el-input-number>
            </el-form-item>
            <el-form-item label="双面打印" prop="sides">
                <el-select v-model="form.sides">
                    <el-option value="one-sided" label="单面打印"></el-option>
                    <el-option value="two-sided-long-edge" label="长边翻页"></el-option>
                    <el-option value="two-sided-short-edge" label="短边翻页"></el-option>
                </el-select>
            </el-form-item>
            <el-form-item label="彩色打印" prop="color">
                <el-select v-model="form.color">
                    <el-option value="False" label="彩色打印"></el-option>
                    <el-option value="True" label="灰度打印"></el-option>
                </el-select>
            </el-form-item>
            <el-form-item label="密码" prop="password">
                <el-input type="password" v-model="form.password" placeholder="请输入密码"></el-input>
            </el-form-item>
            <el-row>
                <el-col :offset="6" :span="12">
                    <el-button round @click="reset_form">重置</el-button>
                    <el-button type="primary" round @click="submit_form">打印</el-button>
                </el-col>
            </el-row>
        </el-form>
    </div>
</template>

<script>
import 'whatwg-fetch';
export default {
    data() {
        return{
            printer_list:[],
            upload_file: [],
            form: {
                printer: '',
                copies: '',
                sides: '',
                color: '',
                token: '',
                password: ''
            },
            form_rules:{
                printer:[
                    {required: true, message: '请选择打印机', trigger: 'blur'}
                ],
                sides:[
                    {required: true, message: '请选择单/双面打印', trigger: 'blur'}
                ],
                color:[
                    {required: true, message: '请选择彩色/灰度打印', trigger: 'blur'}
                ],
                password:[
                    {required: true, message: '请输入打印密码', trigger: 'blur'}
                ],
                copies:[
                    {required: true, message: '请输入打印份数', trigger: 'blur'}
                ]
            }
        }
    },
    created: function(){
        this.get_printers().then(() => {
            this.init_form()
        })
    },
    methods: {
        upload_success: function(response, file, file_list){
            const vm = this
            if(response.status === 'success'){
                this.$message({
                    type: 'success',
                    message: response.message + '，请设置打印参数后，点击打印'
                })
                vm.form.token = response.token
            }else{
                this.$message({
                    type: 'error',
                    message: response.message,
                })
				vm.clear_form()
            }
        },
        upload_exceed: function(files, file_list){
            this.$message({
                type: 'error',
                message: '超出上传限制，请删除旧文件后重新上传'
            })
        },
        get_printers: function(){
            const vm = this
            return fetch('http://127.0.0.1:8888/api/get_printers', {
                method: 'GET',
            }).then(response => {
                return response.json()
            }).then(response => {
                const tmp = []
                response.data.forEach(item => {
                    const tmp_item = {
                        name: item.name,
                        position: item.position
                    }
                    tmp.push(tmp_item)
                })
                vm.printer_list = tmp
            }).catch(error =>{
                vm.$message({
                    'type': 'error',
                    'message': '获取打印机列表失败'
                })
            })
        },
        init_form: function(){
            this.printer_list.forEach(item => {
                if(item.position === '2-315'){
                    this.form.printer = item.name;
                }
            })
            this.form.copies = 1
            this.form.sides = 'two-sided-long-edge'
            this.form.color = 'True'
        },
        reset_form: function(){
            this.$refs.upload.clearFiles()
            this.$refs.form.resetFields()
            this.init_form()
        },
		clear_form: function(){
		    this.$refs.upload.clearFiles()
		    this.$refs.form.resetFields()
		},
        submit_form: function(){
            const vm = this
            if(this.form.token === ''){
                vm.$message({
                    type: 'warning',
                    message: '请上传文件或等待文件上传完成！'
                })
                return
            }
            vm.$refs.form.validate(valid => {
                if(valid){
                    fetch('http://127.0.0.1:8888/api/print', {
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
};

</script>