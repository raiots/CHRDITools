// module.exports = {
//     lang: 'zh-CN',
//     title: 'TasksManager',
//     description: '超好用的任务分配管理系统',
//   }
//
import {defaultTheme, defineUserConfig} from 'vuepress'

export default defineUserConfig({
  lang: 'zh-CN',
  title: 'CHRDITools',
  description: '超好用的任务分配管理系统',
  base: '/static/docs/',

  theme: defaultTheme({
    logo: '/images/logo.png',
    navbar: [
      {
        text: '指南',
        link: '/guide/',
      },
      {
        text: '部署',
        link: '/install/',
      }
    ],
    sidebar: [
      {
        text: '指南',
        children: ['/guide/README.md', '/guide/config.md', '/guide/task_admin.md', '/guide/task_user.md', '/guide/task_eva.md'],
      }
    ],
    repo: 'https://github.com/raiots/CHRDITools',
    repoLabel: '✨Github',
    docsDir: 'docs',
    docsBranch: 'master',
    lastUpdatedText: "📑 最后更新",
    contributorsText: "💕 参与贡献",
    editLinkText: "🖊️ 编辑本文",
    notFound: ["👻 页面不存在"],

  }),
  plugins: [
    ['@vuepress/plugin-medium-zoom', true],
    ['@vuepress/plugin-search', {
    searchMaxSuggestions: 10
  }],
  ]
})

