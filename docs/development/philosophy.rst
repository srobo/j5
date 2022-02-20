Philosophy Behind j5
====================

Some Background
---------------

Student Robotics is a charity that was originally founded by a group of students at the University of Southampton with the goal of bringing the excitement of engineering and the challenge of coding to young people through robotics. This has involved running an annual robotics competition almost every year since 2008, where groups of sixth form students are given some robotics kit, time and mentoring to develop a competitive robot for a unique challenge. In order to reduce the barrier to entry for the competition, it is essential that a knowledge of low level programming and hardware is not required by the students. Thus, a Python API is usually supplied alongside hardware that is developed in order to make things easier.

In 2017 / 18, Student Robotics underwent some restructuring and as a result did not hold a competition. To meet the demand of teachers for the competition, volunteers created two independent competitions SourceBots and Robocon. Both competitions designed and built their own robotics kits that were very similar to the current Student Robotics kit, yet completely incompatible with both each other and the previous kit.

Unification
-----------

Following the reappearance of Student Robotics to the scene in late 2018, there were now three separate, very similar, and also incompatible robotics kits that were being used for the same purpose. None of the kits were perfect, and volunteers didn't want to replicate the effort three times for everything. Thus it makes sense to combine the joint efforts of all three teams of kit developers into one. This is the goal of `j5`. `j5` is a single library that provides a uniform interface and API to students for all three kits. Whilst code will not be directly portable between the kits, it will also not be very hard to port code between them. As a library, `j5` still allows the development teams at the individual competitions to have some degree of customisation over how their kit is used.

Goals
-----

There are some goals behind the `j5` project:

- To be compatible with a variety of relevant current and future robotics kits.
- To use the latest stable version of software and be continuously maintained, even between and during competitions.
- To be an example to students of what good code should look like.
- To unify all existing robotics kits and simulators into one codebase.
- Open by default, no hidden documentation, features or meetings.
