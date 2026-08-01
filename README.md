# nav2_loopback_sim

不依赖物理引擎的轻量 ROS 2 闭环模拟器，用速度积分生成 odom/TF/简化激光，
用于行为树与 Nav2 对照链的快速回归。

> 仓库路径是 `src/sim/loopback_sim`，ROS 包名仍是 `nav2_loopback_sim`。
> 它不是 P2 ROGMap、P3 Nav2-free 或 P4 舵轮动力学的验收环境。

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
| 位姿闭环 | 对输入 `Twist` 做平面运动学积分 |
| 仿真时钟 | 可发布 `/clock` 驱动 `use_sim_time` 节点 |
| TF/odom | 发布导航所需的简化位姿链 |
| 简化激光 | 为 Nav2 costmap 提供基础障碍输入 |
| 重定位注入 | 快速检查路径重算与行为状态变化 |

不包含接触、轮胎侧滑、四舵轮执行器、真实 LiDAR 扫描或 ROGMap 3D ESDF。

## 依赖

- ROS 2 Humble
- `rclpy`、`geometry_msgs`、`nav_msgs`、`tf2_ros`
- `tf_transformations`/`transforms3d`
- 完整对照链还依赖 `ats_sentry_bringup`、`ats_sentry_behavior` 和 Nav2

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

### 通用决策回归

```bash
ros2 launch ats_sentry_bringup loopback_decision_sim.launch.py
```

### 视觉接管专项

```bash
ros2 launch ats_sentry_bringup loopback_vision_test.launch.py
```

### 只观察导航

```bash
ros2 launch ats_sentry_bringup loopback_nav_only.launch.py
```

包内入口包括 `launch/bringup_launch.py`、
`launch/loopback_simulation.launch.py` 和
`launch/tb3_loopback_simulation_launch.py`。正常项目回归优先使用根仓编排入口，
避免漏启动行为参数或速度变换链。

## 接口

| Topic/TF | 方向 | 说明 |
| :--- | :--- | :--- |
| Nav2 command topic | 输入 | 由根 launch remap 决定 |
| odom | 输出 | 积分位姿和速度 |
| `/clock` | 输出 | 可选仿真时钟 |
| scan | 输出 | 简化 2D 激光 |
| TF | 输出 | map/odom/base 的测试链 |

实际 topic 名以 launch remap 和 `params/nav2_params.yaml` 为准。不要把 loopback
topic 存在推断为实机 frame/QoS/timeout 契约已通过。

## 配置与数据流

主配置：`params/nav2_params.yaml`。它服务于 loopback Nav2 对照链，不是实机
总参数，也不应复制 ROGMap/MINCO/MPC 实机参数。

```text
behavior/Nav2 goal
  -> Nav2 planner/controller
  -> cmd_vel compatibility chain
  -> nav2_loopback_sim
  -> integrated odom + TF + scan
  -> Nav2/behavior feedback
```

## 测试边界

适合验证：

- 行为树 XML 是否能执行；
- Nav2 action 是否发送、取消和结束；
- 参数解析、remap、基础 TF 和 topic 接线；
- 视觉接管的目标选择与滞回。

不适合证明：

- ROGMap projection/ESDF 数值正确性；
- MINCO immutable snapshot 和故障租约；
- 四舵轮动力学、跟踪误差、制动距离；
- 物理碰撞或实车性能。

- **已验证**：README 中包名、入口和依赖由 package/launch 静态核对。
- **未验证**：本轮未启动 loopback。
- **未完成**：本包无 Nav2-free action/MINCO/MPC 验收职责，相关工作在 MuJoCo 和实机链完成。

工作区级说明见
[仿真域说明](../../../docs/仿真域说明.md)。

## 参考与致谢

本包用于 ROS 2/Nav2 兼容链的轻量回归。上游 API 和许可证以 ROS 2、Nav2 及仓内
package 声明为准。
