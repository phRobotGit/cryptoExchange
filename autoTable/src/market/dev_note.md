
shedule

1. 大致熟悉数据库结构
futher
    - bak
    - co 
    - trigger
    - cloud
    - user
    - underlying

1个 account 对应多个 type ?
什么是 contract 有效？无效？
select uid, contract_id, position_type, position_layout, side, broker_id, volume, freeze_lock, ctime, lock_time,
status, has_close from co_position;
什么是into_account
transaction中有一个商户id 和 账户 id 概念，有什么区别？ 
    
2. 重新了解业务背景 -> 理解/重构需求
    - 关注 本体、字段、时间等维度、实体等数据粒度
3. 开发代码
    - 流程：SQL -> 实体表 -> 多级实体表 -> 报告+存储 -> 邮件收发
4. dev验证、test验证、上线
