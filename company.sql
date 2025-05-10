-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Vært: mysql
-- Genereringstid: 21. 04 2025 kl. 09:18:22
-- Serverversion: 9.2.0
-- PHP-version: 8.2.27

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `company`
--

DELIMITER $$
--
-- Procedurer
--
CREATE DEFINER=`root`@`%` PROCEDURE `get_users` ()   SELECT * FROM users$$

CREATE DEFINER=`root`@`%` PROCEDURE `get_users_by_name` (IN `name` VARCHAR(20))   SELECT * FROM users WHERE user_name = name$$

CREATE DEFINER=`root`@`%` PROCEDURE `users_by_name_and_last_name` (IN `name` VARCHAR(20), IN `last_name` VARCHAR(20))   SELECT * FROM users WHERE user_name = name AND user_last_name = last_name$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Stand-in-struktur for visning `get_users_with_phones`
-- (Se nedenfor for det aktuelle view)
--
CREATE TABLE `get_users_with_phones` (
`phones` text
,`user_name` varchar(20)
,`user_pk` bigint unsigned
);

-- --------------------------------------------------------

--
-- Struktur-dump for tabellen `items`
--

CREATE TABLE `items` (
  `item_pk` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '0',
  `item_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `item_address` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `item_image` varchar(50) NOT NULL,
  `item_lat` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '0',
  `item_lon` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '0',
  `item_description` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Data dump for tabellen `items`
--

INSERT INTO `items` (`item_pk`, `item_name`, `item_address`, `item_image`, `item_lat`, `item_lon`, `item_description`) VALUES
('8b11f1dc-65fc-4a62-b9c0-e8b83abb5dc9', 'Byens Lopper', 'Værløse 20, 2900', '1.webp', '55.7800', '12.3500', 'Et hyggeligt lokalt loppemarked fyldt med sjove fund, retroting og unikke genbrugsskatte. Perfekt til en lørdagstur med veninderne.'),
('e0a33d1f-731b-47da-a10e-7dfd9d76e2cf', 'Københavns Loppetorv', 'Sønder Boulevard, 1720 København V', '2.webp', '55.6638', '12.5482', 'Et af Vesterbros mest populære udendørs loppemarkeder. Vintage-tøj, møbler og gadestemning i særklasse midt i byen.'),
('d29cd622-1927-475b-9e84-5dfc76f89e90', 'Loppetorv på Frederiksberg', 'Frederiksberg, Smallegade 1, 2000 Frederiksberg', '3.webp', '55.6782', '12.5324', 'Elegant og velorganiseret marked foran rådhuset. Her finder du både designgenbrug, børnetøj og second-hand bøger.'),
('5308e37a-53de-4b1f-960f-28757327ee40', 'Vera\'s Marked Under Buen', 'Studiestræde 27, København K', '4.webp', '55.7083', '12.5422', 'Et ikonisk og moderne loppemarked under Bispeengbuen. Fokus på fashion-forward vintage, upcycled mode og streetwear.'),
('5308e37a-53de-4b1f-960f-28757337ee40', 'Veras fede dyre marked', 'Hellerupvej 29, 2900 Strandvejen', '9.webp', '55.7301', '12.5756', 'Et ikonisk og moderne loppemarked under Bispeengbuen. Fokus på fashion-forward vintage, upcycled mode og streetwear.');

-- --------------------------------------------------------

--
-- Struktur-dump for tabellen `posts`
--

CREATE TABLE `posts` (
  `post_pk` bigint UNSIGNED NOT NULL,
  `post_data` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Data dump for tabellen `posts`
--

INSERT INTO `posts` (`post_pk`, `post_data`) VALUES
(1, 'Post from A'),
(2, 'Post from B');

-- --------------------------------------------------------

--
-- Struktur-dump for tabellen `users`
--

CREATE TABLE `users` (
  `user_pk` bigint UNSIGNED NOT NULL,
  `user_username` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `user_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `user_last_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `user_email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `user_password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `user_created_at` bigint UNSIGNED NOT NULL,
  `user_updated_at` bigint UNSIGNED NOT NULL DEFAULT '0',
  `user_deleted_at` bigint UNSIGNED NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Data dump for tabellen `users`
--

INSERT INTO `users` (`user_pk`, `user_username`, `user_name`, `user_last_name`, `user_email`, `user_password`, `user_created_at`, `user_updated_at`, `user_deleted_at`) VALUES
(8, 'santiago', 'sa', 'do', 'sa@do.com', 'scrypt:32768:8:1$AnzqOsPaGEKsAstq$b18fd8111f02a6a6e18d110728e401640a1740fed877267d3df794dbcefbe59322cffe39e3bc1bf9c92534423c69b7d50e18627cdefddde3654a1842df9d83d8', 1740479110, 0, 0),
(11, 'xxxxxx', 'John', 'Doe', 'mari@sdd.com', 'scrypt:32768:8:1$6objM2mb0hODHnYj$a9504eac4d1085e4f0aed209d1d74e1c18235a3c17ddb8d9d8307ab5f7b4648e07cac6786269f65c2e5e0d0179cc0beeb590d4b8b517cb005272e6edd73636c9', 1740482734, 0, 0),
(13, 'aa', 'aa', 'aaaa', 'z@z.dk', 'scrypt:32768:8:1$luvozeklbL7phYUs$debaf48026327c9ebbe5f63339878c25eb861b6b9e5447d85fb120b2033982fccc8a909df5f49132aae7ee74f2b54da2e5d5afe8965fd015b682d57a6113aae5', 1741952579, 0, 0),
(14, 'ole', 'ole', 'ole', 'ole@ole.dk', 'scrypt:32768:8:1$nNIDvIuZYiI2dP1p$3b82b3eb1a16fb9bf08ff036a04072c9ce8cb7f790fa28506d2594173a0ee9f661e7c5548efa73a8a7524b8a9169fb19c1d670c3869a5673e5211bb7e1302993', 1741952700, 0, 0),
(15, 'michelle', 'michelle', 'enøe', 'm@m.dk', 'scrypt:32768:8:1$slqqjBB5y5SZltiX$051ee7f3fac5fa14fb4480e40efb2e613e9a7161c4b23fbdad8d5d86484d54d36ce40d5b9f872dd09cc51fb6cc8b7684c8e30e595ed6c9330574d03fa79d9ebe', 1741953137, 0, 0),
(17, 'michelle1', 'michelle', 'enøe', 'a@m.dk', 'scrypt:32768:8:1$YFANxs5T2JwsiMbB$4e28dba9624922a6b0429d52fb2bd61357299a3841231849aaab9f788666c044573ba1f3f79f2c43e890c2513f1648701afffcfa47e4c76d66bee6177bf82416', 1741953177, 0, 0),
(20, 'michelle11', 'michelle', 'enøe', 'a@mm.dk', 'scrypt:32768:8:1$6EMYK92HmPhVFOxR$e2f3259671b2dd11c411abb67ddffd253db1960d77085501c4c5f3f7b65c66bde60f352a197b0bcce139d153bd49ca02f71f202efae802017eda38bf634f5a79', 1741953214, 0, 0),
(21, 'simon', 'simon', 'bang', 's@bang.dk', 'scrypt:32768:8:1$EwggKQmLeP4b2HyX$7de1ff6d764f3aface4f41c7ebcc9a743767888f8c18d2f98fe4443841620a2a37c6558447713edbaad14bdd8f4019fa7a278c80e76095c8c570cd78e53840c5', 1741953250, 0, 0),
(24, 'michelleenoe11', 'michelle', 'enøe', 'simon@simon.dk', 'scrypt:32768:8:1$yN8vTEyXrVGugUZF$8ba03aeaeac0f43e7026dcf2baad83cedad50d534ee7e89ee213c30b78f65ad9213df60f6e12d2b4b299181112af1c9eeb04ba849ea5a5a5bb1fcbaa16b4495e', 1742233191, 0, 0),
(25, 'kea', 'kes', 'kes', 'kea@kea.dk', 'scrypt:32768:8:1$plwTxDYIAQMZuocS$36b854ab6c8f604b4d81c1fe39a64fa327c7da996492e36b89c23c256289c4aa5aa13ac446347413df9612cd0b9dd06800c71c6f6dd9cc80237fc9b524eb7674', 1742282587, 0, 0);

--
-- Triggers/udløsere `users`
--
DELIMITER $$
CREATE TRIGGER `update_user` BEFORE UPDATE ON `users` FOR EACH ROW SET NEW.user_updated_at = NOW()
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Struktur-dump for tabellen `users_phones`
--

CREATE TABLE `users_phones` (
  `user_fk` bigint UNSIGNED NOT NULL,
  `user_phone` char(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Data dump for tabellen `users_phones`
--

INSERT INTO `users_phones` (`user_fk`, `user_phone`) VALUES
(1, '111'),
(1, '112'),
(2, '222');

-- --------------------------------------------------------

--
-- Struktur-dump for tabellen `users__posts`
--

CREATE TABLE `users__posts` (
  `user_fk` bigint UNSIGNED NOT NULL,
  `post_fk` bigint UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Data dump for tabellen `users__posts`
--

INSERT INTO `users__posts` (`user_fk`, `post_fk`) VALUES
(1, 1),
(2, 2);

--
-- Begrænsninger for dumpede tabeller
--

--
-- Indeks for tabel `items`
--
ALTER TABLE `items`
  ADD UNIQUE KEY `item_name` (`item_name`);

--
-- Indeks for tabel `posts`
--
ALTER TABLE `posts`
  ADD PRIMARY KEY (`post_pk`),
  ADD UNIQUE KEY `post_pk` (`post_pk`);

--
-- Indeks for tabel `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_pk`),
  ADD UNIQUE KEY `user_pk` (`user_pk`),
  ADD UNIQUE KEY `user_email` (`user_email`),
  ADD UNIQUE KEY `user_username` (`user_username`);

--
-- Indeks for tabel `users_phones`
--
ALTER TABLE `users_phones`
  ADD PRIMARY KEY (`user_fk`,`user_phone`);

--
-- Indeks for tabel `users__posts`
--
ALTER TABLE `users__posts`
  ADD PRIMARY KEY (`user_fk`,`post_fk`),
  ADD KEY `post_fk` (`post_fk`);

--
-- Brug ikke AUTO_INCREMENT for slettede tabeller
--

--
-- Tilføj AUTO_INCREMENT i tabel `posts`
--
ALTER TABLE `posts`
  MODIFY `post_pk` bigint UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Tilføj AUTO_INCREMENT i tabel `users`
--
ALTER TABLE `users`
  MODIFY `user_pk` bigint UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;

-- --------------------------------------------------------

--
-- Struktur for visning `get_users_with_phones`
--
DROP TABLE IF EXISTS `get_users_with_phones`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`%` SQL SECURITY DEFINER VIEW `get_users_with_phones`  AS SELECT `u`.`user_pk` AS `user_pk`, `u`.`user_name` AS `user_name`, group_concat(`p`.`user_phone` order by `p`.`user_phone` ASC separator ',') AS `phones` FROM (`users` `u` left join `users_phones` `p` on((`u`.`user_pk` = `p`.`user_fk`))) GROUP BY `u`.`user_pk` ;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
