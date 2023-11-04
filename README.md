# fuckZXJY
# 职校家园自动打卡

## 更新记录
1. **2023/11/4**
   更新新版本域名
## 使用步骤

1. **增加用户**
  修改users.json
2. **部署到云函数**
  请将依赖一起解压到py根目录并上传云函数
## users.json参数说明

| 参数名              | 示例值                     | 说明                                       |
| ------------------ | -------------------------- | ------------------------------------------ |
| phone_number       | 1700000000                | 手机号码                                   |
| password           | XXXXXXX                  | 密码                                       |
| address            | 上海市浦东新区锦带路       | 地址                                       |
| phonetype          | vivo\|V1923A\|9            | 手机型号                                   |
| longitude          | 121.544296                 | 经度                                       |
| latitude           | 31.221592                  | 纬度                                       |
| pushtoken          | d370a5446ab64c8b8b27e1c4f2b27fbd | Pushplus+推送口令                              |
| modify_coordinates | false/true                      | 是否随机修改坐标最后一位数                               |
| enabled            | false/true                      | 是否启用                                   |
| dToken             | 64c4854504814be08af900b0091bb0480d8a        | 设备标识符(随机生成字符串)                                 |
