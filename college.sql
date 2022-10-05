-- phpMyAdmin SQL Dump
-- version 5.0.3
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 01, 2022 at 05:00 PM
-- Server version: 10.4.14-MariaDB
-- PHP Version: 7.2.34

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `college`
--

-- --------------------------------------------------------

--
-- Table structure for table `attendance`
--

CREATE TABLE `attendance` (
  `a_id` int(11) NOT NULL,
  `a_status` tinyint(4) NOT NULL,
  `a_date` date NOT NULL,
  `s_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `leaves`
--

CREATE TABLE `leaves` (
  `leave_id` int(11) NOT NULL,
  `id` int(11) NOT NULL,
  `reason` varchar(100) NOT NULL,
  `leavetype` varchar(2) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `no_of_leaves` int(11) NOT NULL,
  `display` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `leaves`
--

INSERT INTO `leaves` (`leave_id`, `id`, `reason`, `leavetype`, `start_date`, `end_date`, `no_of_leaves`, `display`) VALUES
(1, 6, 'Sharadi Khansi', 'sl', '2021-11-26', '2021-11-26', 1, 0),
(2, 6, 'Bimari', 'sl', '2021-11-26', '2021-11-26', 1, 0),
(3, 6, 'Travel', 'el', '2021-11-29', '2021-12-10', 10, 0);

-- --------------------------------------------------------

--
-- Table structure for table `parents`
--

CREATE TABLE `parents` (
  `p_id` int(11) NOT NULL,
  `rollno` varchar(25) NOT NULL,
  `s_name` text NOT NULL,
  `p_name` text NOT NULL,
  `s_email` varchar(50) NOT NULL,
  `s_password` varchar(25) NOT NULL,
  `p_email` varchar(50) NOT NULL,
  `p_password` varchar(25) NOT NULL,
  `stream_id` int(11) NOT NULL,
  `sem` int(11) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `parents`
--

INSERT INTO `parents` (`p_id`, `rollno`, `s_name`, `p_name`, `s_email`, `s_password`, `p_email`, `p_password`, `stream_id`, `sem`) VALUES
(1, 'IGNUVAD21CSETONY1A', 'Tony Stark', 'Howard Stark', 'tony.stark3000@starkindustires.com', 'IamIronMan', 'howard.stark3000@starkindustires.com', 'WeLoveYou3000', 1, 2);

-- --------------------------------------------------------

--
-- Table structure for table `remarks`
--

CREATE TABLE `remarks` (
  `remarkid` int(11) NOT NULL,
  `remarks` varchar(100) NOT NULL,
  `s_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `results`
--

CREATE TABLE `results` (
  `result_id` int(11) NOT NULL,
  `test_id` int(11) NOT NULL,
  `s_id` int(11) NOT NULL,
  `given_marks` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `stream`
--

CREATE TABLE `stream` (
  `stream_id` int(11) NOT NULL,
  `stream` text NOT NULL,
  `duration` int(11) NOT NULL,
  `course` text NOT NULL,
  `fees` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `stream`
--

INSERT INTO `stream` (`stream_id`, `stream`, `duration`, `course`, `fees`) VALUES
(1, 'Computer Science', 8, 'B. Tech', 50000),
(2, 'History', 2, 'Archeology', 10000),
(3, 'Physics', 6, 'B. Sc', 30000),
(8, 'Accounts', 6, 'B. Com', 20000),
(9, 'Civil Engg.', 4, 'B.Tech', 30000);

-- --------------------------------------------------------

--
-- Table structure for table `studentleave`
--

CREATE TABLE `studentleave` (
  `leave_id` int(11) NOT NULL,
  `from_date` date NOT NULL,
  `to_date` date NOT NULL,
  `no_of_days` int(11) NOT NULL,
  `reason` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `subjects`
--

CREATE TABLE `subjects` (
  `subject_id` int(11) NOT NULL,
  `subject` text NOT NULL,
  `stream_id` int(11) NOT NULL,
  `sem` int(2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `subjects`
--

INSERT INTO `subjects` (`subject_id`, `subject`, `stream_id`, `sem`) VALUES
(1, 'Java', 1, 4),
(2, 'History of Westeros', 2, 2),
(3, 'Relativity', 3, 3),
(5, 'Digital Electronics', 1, 3),
(14, 'Marketing', 8, 1),
(15, 'Basic Civil Engg.', 9, 1);

-- --------------------------------------------------------

--
-- Table structure for table `tests`
--

CREATE TABLE `tests` (
  `test_id` int(11) NOT NULL,
  `test_name` varchar(25) NOT NULL,
  `topics` varchar(100) NOT NULL,
  `subject_id` int(11) NOT NULL,
  `total_marks` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `updates`
--

CREATE TABLE `updates` (
  `update_id` int(11) NOT NULL,
  `faculty_id` int(11) NOT NULL,
  `note_update` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` text NOT NULL,
  `username` varchar(25) NOT NULL,
  `password` varchar(25) DEFAULT NULL,
  `email` varchar(50) NOT NULL,
  `subjects` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`subjects`)),
  `salary` bigint(20) NOT NULL DEFAULT 0,
  `is_superuser` tinyint(1) NOT NULL DEFAULT 0,
  `sl` int(2) NOT NULL DEFAULT 0,
  `cl` int(2) NOT NULL DEFAULT 0,
  `el` int(2) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `username`, `password`, `email`, `subjects`, `salary`, `is_superuser`, `sl`, `cl`, `el`) VALUES
(1, 'Harshal ', 'Admin123', '7heW4r10ck', 'admin_harshal@gmail.com', '{\"subjects\": []}', 0, 1, 8, 7, 16),
(6, 'Jon Snow', 'Jon169', 'YouKnowNothing', 'jonsnow@thewall.com', '{\"subjects\": [2]}', 12300, 0, 6, 7, 4),
(14, 'Albert Einstein', 'Albert37', 'TimeIsRelative69', 'alberteinstein@abcd.com', '{\"subjects\": [1, 3, 5]}', 123456, 0, 8, 7, 16),
(16, 'Harshal Faculty', 'Harshal666', 'Harshal6969', 'harshal@faculty.com', '{\"subjects\": [1, 5]}', 12345, 0, 8, 7, 16),
(19, 'Vivek Bindra', 'Vivek36', 'WVtXnGqM', 'vivekbindra@business.com', '{\"subjects\": [14]}', 12345, 0, 8, 7, 16),
(20, 'Jitu Bhaiya', 'Jitu764', 'OmWvEDqs', 'jitubhaiya@aimers.com', '{\"subjects\": [3]}', 54321, 0, 8, 7, 16),
(21, 'Laeke Dhrumil', 'Laeke318', 'CGUgJijh', 'laeke_aana@itmvu.in', '{\"subjects\": [15]}', 150, 0, 8, 7, 16);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `attendance`
--
ALTER TABLE `attendance`
  ADD PRIMARY KEY (`a_id`);

--
-- Indexes for table `leaves`
--
ALTER TABLE `leaves`
  ADD PRIMARY KEY (`leave_id`),
  ADD KEY `FOREIGN` (`id`);

--
-- Indexes for table `parents`
--
ALTER TABLE `parents`
  ADD PRIMARY KEY (`p_id`);

--
-- Indexes for table `remarks`
--
ALTER TABLE `remarks`
  ADD PRIMARY KEY (`remarkid`);

--
-- Indexes for table `results`
--
ALTER TABLE `results`
  ADD PRIMARY KEY (`result_id`);

--
-- Indexes for table `stream`
--
ALTER TABLE `stream`
  ADD PRIMARY KEY (`stream_id`);

--
-- Indexes for table `subjects`
--
ALTER TABLE `subjects`
  ADD PRIMARY KEY (`subject_id`),
  ADD KEY `foreign key` (`stream_id`);

--
-- Indexes for table `tests`
--
ALTER TABLE `tests`
  ADD PRIMARY KEY (`test_id`);

--
-- Indexes for table `updates`
--
ALTER TABLE `updates`
  ADD PRIMARY KEY (`update_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `attendance`
--
ALTER TABLE `attendance`
  MODIFY `a_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `leaves`
--
ALTER TABLE `leaves`
  MODIFY `leave_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `parents`
--
ALTER TABLE `parents`
  MODIFY `p_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `remarks`
--
ALTER TABLE `remarks`
  MODIFY `remarkid` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `results`
--
ALTER TABLE `results`
  MODIFY `result_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `stream`
--
ALTER TABLE `stream`
  MODIFY `stream_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `subjects`
--
ALTER TABLE `subjects`
  MODIFY `subject_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `tests`
--
ALTER TABLE `tests`
  MODIFY `test_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `updates`
--
ALTER TABLE `updates`
  MODIFY `update_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `leaves`
--
ALTER TABLE `leaves`
  ADD CONSTRAINT `FOREIGN` FOREIGN KEY (`id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `subjects`
--
ALTER TABLE `subjects`
  ADD CONSTRAINT `foreign key` FOREIGN KEY (`stream_id`) REFERENCES `stream` (`stream_id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
