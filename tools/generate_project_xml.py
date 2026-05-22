from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from pathlib import Path
import xml.etree.ElementTree as ET


NS = "http://schemas.microsoft.com/project"
ET.register_namespace("", NS)

WORK_MINUTES_PER_DAY = 8 * 60
CAL_NAME = "Standard"
DEFAULT_START = datetime(2026, 5, 18, 8, 0, 0)


@dataclass
class Pred:
    code: str
    kind: int = 1
    lag_days: float = 0.0


@dataclass
class TaskInput:
    code: str
    name: str
    duration_days: float
    owner: str
    preds: list[Pred] = field(default_factory=list)
    percent_complete: int = 0


@dataclass
class ModuleInput:
    name: str
    tasks: list[TaskInput]


@dataclass
class ScheduledTask:
    code: str
    name: str
    owner: str
    outline_number: str
    outline_level: int
    duration_minutes: int
    work_minutes: int
    start_offset: int
    finish_offset: int
    preds: list[Pred]
    percent_complete: int
    is_summary: bool = False
    notes: str = ""
    uid: int = 0
    id: int = 0


MODULES: list[ModuleInput] = [
    ModuleInput(
        name="讲师信息管理",
        tasks=[
            TaskInput("A1", "管理讲师资料UI设计", 0.5, "程序员A", percent_complete=100),
            TaskInput("A2", "管理讲师资料前端开发", 1.0, "程序员E", preds=[Pred("A1")], percent_complete=100),
            TaskInput("A3", "管理讲师资料后端开发", 1.0, "程序员D", preds=[Pred("A1"), Pred("A4", kind=0, lag_days=-0.2)], percent_complete=60),
            TaskInput("A4", "讲师资料数据库设计", 0.3, "程序员C", preds=[Pred("A1", kind=2)], percent_complete=100),
            TaskInput("A5", "管理讲师资料前后端集成测试", 0.2, "程序员C", preds=[Pred("A2"), Pred("A3", kind=3)], percent_complete=0),
        ],
    ),
    ModuleInput(
        name="授课信息管理",
        tasks=[
            TaskInput("B1", "管理授课信息UI设计", 0.5, "程序员B", preds=[Pred("A5", lag_days=0.2)], percent_complete=100),
            TaskInput("B2", "管理授课信息前端开发", 0.6, "程序员A", preds=[Pred("B1")], percent_complete=100),
            TaskInput("B3", "管理授课信息后端开发", 0.8, "程序员E", preds=[Pred("B1"), Pred("B4", kind=0)], percent_complete=45),
            TaskInput("B4", "授课记录数据库设计", 0.2, "程序员D", preds=[Pred("B1", kind=2)], percent_complete=100),
            TaskInput("B5", "管理授课信息前、后端集成测试", 0.4, "程序员D", preds=[Pred("B2"), Pred("B3", kind=3)], percent_complete=0),
        ],
    ),
    ModuleInput(
        name="学员签到管理",
        tasks=[
            TaskInput("C1", "签到UI设计", 0.5, "程序员C", preds=[Pred("B5", lag_days=0.1)], percent_complete=100),
            TaskInput("C2", "签到前端开发", 0.3, "程序员B", preds=[Pred("C1")], percent_complete=100),
            TaskInput("C3", "签到后端开发", 0.5, "程序员A", preds=[Pred("C1"), Pred("C4", kind=0)], percent_complete=20),
            TaskInput("C4", "签到信息数据库设计", 0.2, "程序员E", preds=[Pred("C1", kind=2)], percent_complete=100),
            TaskInput("C5", "签到前后端集成测试", 0.3, "程序员A", preds=[Pred("C2"), Pred("C3", kind=3)], percent_complete=0),
        ],
    ),
    ModuleInput(
        name="培训报名",
        tasks=[
            TaskInput("D1", "培训报名UI设计", 0.4, "程序员D", preds=[Pred("C5", lag_days=0.1)], percent_complete=100),
            TaskInput("D2", "培训报名前端开发", 0.5, "程序员C", preds=[Pred("D1")], percent_complete=70),
            TaskInput("D3", "培训报名后端开发", 0.5, "程序员B", preds=[Pred("D1", kind=2)], percent_complete=35),
            TaskInput("D4", "培训报名前后端集成测试", 1.0, "程序员B", preds=[Pred("D2"), Pred("D3", kind=3)], percent_complete=0),
        ],
    ),
]


def fmt_dt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def duration_xml_from_minutes(minutes: int) -> str:
    hours, mins = divmod(minutes, 60)
    return f"PT{hours}H{mins}M0S"


def lag_xml(days: float) -> int:
    # Project XML stores LinkLag in tenths of a minute.
    return round(days * WORK_MINUTES_PER_DAY * 10)


def minutes_from_days(days: float) -> int:
    return round(days * WORK_MINUTES_PER_DAY)


def add_weekdays(start_day: date, weekdays: int) -> date:
    current = start_day
    moved = 0
    while moved < weekdays:
        current += timedelta(days=1)
        if current.weekday() < 5:
            moved += 1
    return current


def offset_to_datetime(offset_minutes: int) -> datetime:
    if offset_minutes < 0:
        offset_minutes = 0
    day_index, minute_of_day = divmod(offset_minutes, WORK_MINUTES_PER_DAY)
    base_day = add_weekdays(DEFAULT_START.date(), day_index)
    if minute_of_day < 240:
        hour = 8 + minute_of_day // 60
        minute = minute_of_day % 60
    elif minute_of_day == 240:
        hour = 12
        minute = 0
    else:
        minute_of_afternoon = minute_of_day - 240
        hour = 13 + minute_of_afternoon // 60
        minute = minute_of_afternoon % 60
    return datetime.combine(base_day, time(hour=hour, minute=minute))


def summary_percent(tasks: list[ScheduledTask]) -> int:
    total = sum(t.work_minutes for t in tasks)
    if total == 0:
        return 0
    done = sum(round(t.work_minutes * t.percent_complete / 100) for t in tasks)
    return round(done * 100 / total)


def schedule_leaf_tasks() -> tuple[list[ScheduledTask], dict[str, ScheduledTask]]:
    display_items: list[tuple[int, int, TaskInput]] = []
    for module_idx, module in enumerate(MODULES, start=1):
        for task_idx, task in enumerate(module.tasks, start=1):
            display_items.append((module_idx, task_idx, task))

    remaining = {item.code: item for _, _, item in display_items}
    offsets: dict[str, tuple[int, int]] = {}

    while remaining:
        progressed = False
        for code, item in list(remaining.items()):
            if not all(pred.code in offsets for pred in item.preds):
                continue
            duration = minutes_from_days(item.duration_days)
            constraints: list[int] = [0]
            for pred in item.preds:
                pred_start, pred_finish = offsets[pred.code]
                lag = minutes_from_days(pred.lag_days)
                if pred.kind == 1:  # FS
                    constraints.append(pred_finish + lag)
                elif pred.kind == 3:  # SS
                    constraints.append(pred_start + lag)
                elif pred.kind == 0:  # FF
                    constraints.append(pred_finish + lag - duration)
                elif pred.kind == 2:  # SF
                    constraints.append(pred_start + lag - duration)
            start_offset = max(constraints)
            finish_offset = start_offset + duration
            offsets[code] = (start_offset, finish_offset)
            del remaining[code]
            progressed = True
        if not progressed:
            unresolved = ", ".join(sorted(remaining))
            raise RuntimeError(f"无法解析任务前置关系，疑似存在循环依赖：{unresolved}")

    scheduled: list[ScheduledTask] = []
    by_code: dict[str, ScheduledTask] = {}
    for module_idx, task_idx, item in display_items:
        start_offset, finish_offset = offsets[item.code]
        task = ScheduledTask(
            code=item.code,
            name=f"{item.code} {item.name}",
            owner=item.owner,
            outline_number=f"{module_idx}.{task_idx}",
            outline_level=2,
            duration_minutes=finish_offset - start_offset,
            work_minutes=finish_offset - start_offset,
            start_offset=start_offset,
            finish_offset=finish_offset,
            preds=item.preds,
            percent_complete=item.percent_complete,
            notes=f"责任人：{item.owner}",
        )
        scheduled.append(task)
        by_code[item.code] = task
    return scheduled, by_code


def build_scheduled_tasks(percent_mode: bool) -> tuple[list[ScheduledTask], dict[str, int], dict[str, int], int]:
    leaf_tasks, by_code = schedule_leaf_tasks()
    resource_uid_by_name = {name: idx for idx, name in enumerate(sorted({t.owner for t in leaf_tasks}), start=1)}

    tasks: list[ScheduledTask] = []
    next_uid = 1
    next_id = 1
    module_uid_by_name: dict[str, int] = {}

    for module_idx, module in enumerate(MODULES, start=1):
        children = [by_code[item.code] for item in module.tasks]
        start_offset = min(t.start_offset for t in children)
        finish_offset = max(t.finish_offset for t in children)
        summary = ScheduledTask(
            code=f"S{module_idx}",
            name=module.name,
            owner="",
            outline_number=str(module_idx),
            outline_level=1,
            duration_minutes=finish_offset - start_offset,
            work_minutes=sum(t.work_minutes for t in children),
            start_offset=start_offset,
            finish_offset=finish_offset,
            preds=[],
            percent_complete=summary_percent(children) if percent_mode else 0,
            is_summary=True,
        )
        summary.uid = next_uid
        summary.id = next_id
        tasks.append(summary)
        module_uid_by_name[module.name] = summary.uid
        next_uid += 1
        next_id += 1
        for child in children:
            child.uid = next_uid
            child.id = next_id
            tasks.append(child)
            next_uid += 1
            next_id += 1

    finish_offset = max(task.finish_offset for task in tasks if not task.is_summary)
    return tasks, resource_uid_by_name, module_uid_by_name, finish_offset


def add_text(parent: ET.Element, tag: str, text: str | int | float) -> ET.Element:
    el = ET.SubElement(parent, f"{{{NS}}}{tag}")
    el.text = str(text)
    return el


def build_project(percent_mode: bool) -> ET.ElementTree:
    now = datetime(2026, 5, 12, 9, 0, 0)
    scheduled_tasks, resource_uid_by_name, _, finish_offset = build_scheduled_tasks(percent_mode)
    project_finish = offset_to_datetime(finish_offset)
    project = ET.Element(f"{{{NS}}}Project")

    add_text(project, "Name", "软件过程与项目管理实验2-项目开发计划")
    add_text(project, "Title", "实验2 第四部分 甘特图源文件")
    add_text(project, "Author", "Codex")
    add_text(project, "CreationDate", fmt_dt(now))
    add_text(project, "LastSaved", fmt_dt(now))
    add_text(project, "ScheduleFromStart", 1)
    add_text(project, "StartDate", fmt_dt(DEFAULT_START))
    add_text(project, "FinishDate", fmt_dt(project_finish))
    add_text(project, "FYStartDate", 1)
    add_text(project, "CriticalSlackLimit", 0)
    add_text(project, "CurrencyDigits", 2)
    add_text(project, "CurrencySymbol", "¥")
    add_text(project, "CurrencyCode", "CNY")
    add_text(project, "DefaultTaskType", 1)
    add_text(project, "DefaultFixedCostAccrual", 3)
    add_text(project, "DefaultStandardRate", 0)
    add_text(project, "DefaultOvertimeRate", 0)
    add_text(project, "DurationFormat", 7)
    add_text(project, "WorkFormat", 2)
    add_text(project, "EditableActualCosts", 0)
    add_text(project, "HonorConstraints", 0)
    add_text(project, "InsertedProjectsLikeSummary", 0)
    add_text(project, "MultipleCriticalPaths", 0)
    add_text(project, "NewTasksEffortDriven", 0)
    add_text(project, "NewTasksEstimated", 0)
    add_text(project, "SplitsInProgressTasks", 0)
    add_text(project, "SpreadActualCost", 0)
    add_text(project, "SpreadPercentComplete", 0)
    add_text(project, "TaskUpdatesResource", 1)
    add_text(project, "FiscalYearStart", 0)
    add_text(project, "WeekStartDay", 1)
    add_text(project, "MoveCompletedEndsBack", 0)
    add_text(project, "MoveRemainingStartsBack", 0)
    add_text(project, "MoveRemainingStartsForward", 0)
    add_text(project, "MoveCompletedEndsForward", 0)
    add_text(project, "BaselineForEarnedValue", 0)
    add_text(project, "AutoAddNewResourcesAndTasks", 1)
    add_text(project, "StatusDate", fmt_dt(offset_to_datetime(minutes_from_days(4))))
    add_text(project, "CurrentDate", fmt_dt(now))
    add_text(project, "MicrosoftProjectServerURL", "")
    add_text(project, "Autolink", 1)
    add_text(project, "NewTaskStartDate", 0)
    add_text(project, "DefaultTaskEVMethod", 0)
    add_text(project, "ExtendedCreationDate", fmt_dt(now))
    add_text(project, "ActualsInSync", 0)
    add_text(project, "ProjectExternallyEdited", 0)
    add_text(project, "RemoveFileProperties", 0)
    add_text(project, "AdminProject", 0)
    add_text(project, "NameView", "")
    add_text(project, "TimescaleStart", fmt_dt(DEFAULT_START))
    add_text(project, "TimescaleFinish", fmt_dt(project_finish + timedelta(days=2)))
    add_text(project, "MinutesPerDay", WORK_MINUTES_PER_DAY)
    add_text(project, "MinutesPerWeek", WORK_MINUTES_PER_DAY * 5)
    add_text(project, "DaysPerMonth", 20)
    add_text(project, "DefaultStartTime", "08:00:00")
    add_text(project, "DefaultFinishTime", "17:00:00")
    add_text(project, "DefaultTaskMode", 0)
    add_text(project, "DefaultCalendarUID", 1)
    add_text(project, "SaveVersion", 15)

    calendars = ET.SubElement(project, f"{{{NS}}}Calendars")
    cal = ET.SubElement(calendars, f"{{{NS}}}Calendar")
    add_text(cal, "UID", 1)
    add_text(cal, "Name", CAL_NAME)
    add_text(cal, "IsBaseCalendar", 1)
    add_text(cal, "BaseCalendarUID", -1)
    week_days = ET.SubElement(cal, f"{{{NS}}}WeekDays")
    for day_type in range(1, 8):
        wd = ET.SubElement(week_days, f"{{{NS}}}WeekDay")
        add_text(wd, "DayType", day_type)
        working = 1 if day_type in range(2, 7) else 0
        add_text(wd, "DayWorking", working)
        if working:
            wts = ET.SubElement(wd, f"{{{NS}}}WorkingTimes")
            for start, finish in (("08:00:00", "12:00:00"), ("13:00:00", "17:00:00")):
                wt = ET.SubElement(wts, f"{{{NS}}}WorkingTime")
                add_text(wt, "FromTime", start)
                add_text(wt, "ToTime", finish)

    resources = ET.SubElement(project, f"{{{NS}}}Resources")
    resource_work: dict[str, int] = {name: 0 for name in resource_uid_by_name}
    for task in scheduled_tasks:
        if not task.is_summary and task.owner:
            resource_work[task.owner] += task.work_minutes

    for name, idx in resource_uid_by_name.items():
        res = ET.SubElement(resources, f"{{{NS}}}Resource")
        add_text(res, "UID", idx)
        add_text(res, "ID", idx)
        add_text(res, "Name", name)
        add_text(res, "Type", 1)
        add_text(res, "IsNull", 0)
        add_text(res, "Active", 1)
        add_text(res, "Initials", name[-1])
        add_text(res, "MaxUnits", 1)
        add_text(res, "PeakUnits", 1)
        add_text(res, "CalendarUID", 1)
        add_text(res, "CanLevel", 1)
        add_text(res, "AccrueAt", 3)
        add_text(res, "StandardRate", 0)
        add_text(res, "OvertimeRate", 0)
        add_text(res, "CostPerUse", 0)
        add_text(res, "Work", duration_xml_from_minutes(resource_work[name]))
        add_text(res, "RegularWork", duration_xml_from_minutes(resource_work[name]))
        add_text(res, "RemainingWork", duration_xml_from_minutes(resource_work[name]))

    tasks = ET.SubElement(project, f"{{{NS}}}Tasks")
    code_to_uid = {task.code: task.uid for task in scheduled_tasks if not task.is_summary}
    for item in scheduled_tasks:
        task = ET.SubElement(tasks, f"{{{NS}}}Task")
        add_text(task, "UID", item.uid)
        add_text(task, "ID", item.id)
        add_text(task, "Name", item.name)
        add_text(task, "Type", 1)
        add_text(task, "IsNull", 0)
        add_text(task, "Active", 1)
        add_text(task, "CreateDate", fmt_dt(now))
        add_text(task, "WBS", item.code if not item.is_summary else item.outline_number)
        add_text(task, "OutlineNumber", item.outline_number)
        add_text(task, "OutlineLevel", item.outline_level)
        add_text(task, "Priority", 500)
        add_text(task, "Start", fmt_dt(offset_to_datetime(item.start_offset)))
        add_text(task, "Finish", fmt_dt(offset_to_datetime(item.finish_offset)))
        add_text(task, "Duration", duration_xml_from_minutes(item.duration_minutes))
        add_text(task, "DurationFormat", 7)
        if item.is_summary:
            add_text(task, "Work", duration_xml_from_minutes(item.work_minutes))
            add_text(task, "RemainingWork", duration_xml_from_minutes(item.work_minutes))
            add_text(task, "Summary", 1)
        else:
            percent = item.percent_complete if percent_mode else 0
            actual_minutes = round(item.work_minutes * percent / 100)
            remaining_minutes = item.work_minutes - actual_minutes
            add_text(task, "Work", duration_xml_from_minutes(item.work_minutes))
            add_text(task, "RemainingDuration", duration_xml_from_minutes(remaining_minutes))
            add_text(task, "RemainingWork", duration_xml_from_minutes(remaining_minutes))
            add_text(task, "Summary", 0)
            add_text(task, "Notes", item.notes)
            add_text(task, "PercentComplete", percent)
            add_text(task, "PercentWorkComplete", percent)
            add_text(task, "ActualDuration", duration_xml_from_minutes(actual_minutes))
            add_text(task, "ActualWork", duration_xml_from_minutes(actual_minutes))
            if percent_mode and percent > 0:
                add_text(task, "ActualStart", fmt_dt(offset_to_datetime(item.start_offset)))
            if percent_mode and percent == 100:
                add_text(task, "ActualFinish", fmt_dt(offset_to_datetime(item.finish_offset)))
            for pred in item.preds:
                pred_link = ET.SubElement(task, f"{{{NS}}}PredecessorLink")
                add_text(pred_link, "PredecessorUID", code_to_uid[pred.code])
                add_text(pred_link, "Type", pred.kind)
                add_text(pred_link, "CrossProject", 0)
                add_text(pred_link, "LinkLag", lag_xml(pred.lag_days))
                add_text(pred_link, "LagFormat", 7)
        add_text(task, "Manual", 0)
        add_text(task, "Milestone", 0)
        add_text(task, "Critical", 0)
        add_text(task, "FixedCostAccrual", 3)
        add_text(task, "ConstraintType", 0)
        add_text(task, "CalendarUID", 1)
        add_text(task, "IgnoreResourceCalendar", 0)
        add_text(task, "HideBar", 0)
        add_text(task, "Rollup", 0)
        add_text(task, "Estimated", 0)

    assignments = ET.SubElement(project, f"{{{NS}}}Assignments")
    assignment_uid = 1
    for item in scheduled_tasks:
        if item.is_summary:
            continue
        percent = item.percent_complete if percent_mode else 0
        actual_minutes = round(item.work_minutes * percent / 100)
        remaining_minutes = item.work_minutes - actual_minutes
        assn = ET.SubElement(assignments, f"{{{NS}}}Assignment")
        add_text(assn, "UID", assignment_uid)
        add_text(assn, "TaskUID", item.uid)
        add_text(assn, "ResourceUID", resource_uid_by_name[item.owner])
        add_text(assn, "PercentWorkComplete", percent)
        add_text(assn, "ActualWork", duration_xml_from_minutes(actual_minutes))
        add_text(assn, "RemainingWork", duration_xml_from_minutes(remaining_minutes))
        add_text(assn, "Work", duration_xml_from_minutes(item.work_minutes))
        add_text(assn, "Units", 1)
        add_text(assn, "Start", fmt_dt(offset_to_datetime(item.start_offset)))
        add_text(assn, "Finish", fmt_dt(offset_to_datetime(item.finish_offset)))
        add_text(assn, "Delay", 0)
        add_text(assn, "WorkContour", 0)
        add_text(assn, "HasFixedRateUnits", 1)
        assignment_uid += 1

    return ET.ElementTree(project)


def indent(elem: ET.Element, level: int = 0) -> None:
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for child in elem:
            indent(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = i
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i


def main() -> None:
    out_dir = Path("/Users/bytedance/Desktop/Projects/myBlog/output")
    out_dir.mkdir(parents=True, exist_ok=True)

    plan_tree = build_project(percent_mode=False)
    progress_tree = build_project(percent_mode=True)

    for path, tree in (
        (out_dir / "project_plan_for_project2013.xml", plan_tree),
        (out_dir / "project_progress_for_project2013.xml", progress_tree),
    ):
        indent(tree.getroot())
        tree.write(path, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    main()
