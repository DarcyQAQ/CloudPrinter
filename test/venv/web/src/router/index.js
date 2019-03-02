
let routes = [
    {
        path: '/404',
        component: (resolve) => require(['@/views/404.vue'], resolve),
        name: '',
        hidden: true
    },
	{
	    path: '/admin',
	    component: (resolve) => require(['@/views/Admin.vue'], resolve),
// 	    name: '',
// 	    iconCls: 'fa fa-home',
// 	    leaf: true,
// 	    redirect: '/admin',
// 	    children: [
// 	        {path: '/admin', component: (resolve) => require(['@/views/Admin.vue'], resolve), name: ''}
// 	    ]
	},
    {
        path: '/index',
        component: (resolve) => require(['@/views/Home.vue'], resolve),
        name: '主页',
        iconCls: 'fa fa-home',
        leaf: true,
        redirect: '/index',
        children: [
            {path: '/index', component: (resolve) => require(['@/views/Index.vue'], resolve), name: '状态'}
        ]
    },
    {
        path: '*',
        hidden: true,
        redirect: { path: '/404' }
    },
];

export default routes;