# ATS loopback simulator

不依赖物理引擎的轻量 ROS 2 闭环模拟器，用速度积分生成 odom/TF/简化激光，
用于静态地图、TF/odom 与 `cmd_vel_arbiter -> /cmd_vel/selected` 速度出口接线的快速回归。

> 仓库路径是 `src/sim/loopback_sim`，ROS 包名仍是 `nav2_loopback_sim`。
> 它不是 P2 ROGMap、P3 行为闭环或 P4 舵轮动力学的验收环境。

## 目录

- [功能模块](#功能模块)
- [依赖](#依赖)
- [Quick Start](#quick-start)
- [启动入口](#启动入口)
- [接口](#接口)
- [配置与数据流](#配置与数据流)
- [测试边界](#测试边界)
- [参考与致谢](#参考与致谢)

## 功能模块

| 功能 | 说明 |
| :--- | :--- |
| 位姿闭环 | 对 `/cmd_vel/selected` 的 `Twist` 做平面运动学积分 |
| 速度仲裁 | launch 同时启动 `cmd_vel_arbiter`，与实机/MuJoCo/Gazebo 共用“执行端只消费 selected”契约 |
| 仿真时钟 | 可发布 `/clock` 驱动 `use_sim_time` 节点 |
| TF/odom | 发布导航所需的简化位姿链 |
| 简化激光 | 按 `/map` 的静态占据栅格生成基础障碍输入 |
| 重定位注入 | 快速检查路径重算与行为状态变化 |

不包含接触、轮胎侧滑、四舵轮执行器、真实 LiDAR 扫描或 ROGMap 3D ESDF。

## 依赖

- ROS 2 Humble
- `rclpy`、`geometry_msgs`、`nav_msgs`、`tf2_ros`
- `tf_transformations`/`transforms3d`
- `ats_nav_bringup` 的 `static_map_publisher.py`
- `ats_cmd_vel_arbiter` 的 `cmd_vel_arbiter_node`

## Quick Start

```bash
cd /home/ats/ATS_2026_snetry_test
source /opt/ros/humble/setup.bash
colcon build --base-paths src \
  --packages-select nav2_loopback_sim \
  --symlink-install
source install/setup.bash
```

## 启动入口

```bash
ros2 launch nav2_loopback_sim loopback_simulation.launch.py
```

| Launch 参数 | 默认值 | 说明 |
| :--- | :--- | :--- |
| `map` | `share/nav2_loopback_sim/maps/warehouse.yaml` | 发布到 `/map` 的静态栅格 YAML |
| `scan_frame_id` | `base_scan` | 简化激光 frame |

该入口以 `ats_nav_bringup/static_map_publisher.py` 发布 `/map`（`reliable +
transient_local`），并启动 `cmd_vel_arbiter`（manual `/cmd_vel`、autonomy
`/cmd_vel/autonomy_raw`、selected `/cmd_vel/selected`、`require_serial_link:=False`）。
loopback 只消费 `/cmd_vel/selected`（`enable_stamped_cmd_vel:=False`，arbiter 发布未打戳
`Twist`），并输出 `odom`、TF、`scan`。它不启动导航、定位、规划或 MPC 节点。

手动速度直接发到 `/cmd_vel` 即可经 arbiter 放行；autonomy 源需要 arbiter 的
`ExecutionCommand` 授权、planner status 与 map ready，loopback 本身不提供这些输入。
不要再向 `/motion_control` 发速度，loopback 已不订阅该话题。

## 接口

| Topic/TF | 方向 | 说明 |
| :--- | :--- | :--- |
| `/cmd_vel` | 输入（arbiter） | 手动速度源（`geometry_msgs/Twist`） |
| `/cmd_vel/autonomy_raw` | 输入（arbiter） | 自动速度源，需授权 |
| `/cmd_vel/selected` | arbiter 输出 / loopback 输入 | 唯一执行端速度输入，参数 `command_topic` |
| `/map` | 输入 | 静态图，reliable + transient-local |
| odom | 输出 | 积分位姿和速度 |
| `/clock` | 输出 | 可选仿真时钟 |
| scan | 输出 | 简化 2D 激光 |
| TF | 输出 | map/odom/base 的测试链 |

不要把 loopback topic 存在推断为实机 frame/QoS/timeout 契约已通过。

## 配置与数据流

```text
/map -> static_map_publisher -> loopback_simulator -> scan
/cmd_vel + /cmd_vel/autonomy_raw -> cmd_vel_arbiter -> /cmd_vel/selected
/cmd_vel/selected -> loopback_simulator -> integrated odom + TF
```

## 测试边界

适合验证：

- 静态图 transient-local QoS、基础 TF 和 `cmd_vel_arbiter -> /cmd_vel/selected` 接线；
- `/map` 栅格到简化 scan 的几何遍历。

不适合证明：

- ROGMap projection/ESDF 数值正确性；
- MINCO immutable snapshot 和故障租约；
- 四舵轮动力学、跟踪误差、制动距离；
- 物理碰撞或实车性能。

- **已验证**：README 中包名、入口和依赖由 package/launch 静态核对。
- **未验证**：本轮未启动 loopback。
- **未完成**：本包不承担 action/MINCO/MPC 验收职责，相关工作在 MuJoCo 链完成。

工作区级说明见
[仿真域说明](../../../docs/仿真域说明.md)。

## 参考与致谢

本包用于 ROS 2 轻量回归。上游 API 和许可证以仓内 package 声明为准。
