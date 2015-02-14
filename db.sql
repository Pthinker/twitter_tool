USE `twitter_tool`;

DROP TABLE IF EXISTS `sender_account`;
create table `sender_account` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `sender_twitter_id` BIGINT(20) NOT NULL,
    `sender_twitter_handle` varchar(50) NOT NULL,
    `gco_internal_id` varchar(50),
    `triggered_from` varchar(50),
    `sender_data` TEXT,
    `created_at` TIMESTAMP, 
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `sender_following`;
create table `sender_following` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `sender_twitter_id` BIGINT(20) NOT NULL,
    `following` TEXT,
    `created_at` TIMESTAMP, 
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `twitter_id_to_handle`;
create table `twitter_id_to_handle` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `twitter_id` BIGINT(20) NOT NULL,
    `twitter_handle` varchar(50),
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `operations`;
create table `operations` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `account` VARCHAR(50),
    `is_closed` BOOL DEFAULT '0',
    `user_id` BIGINT(20),
    `user_gco_internal_id` varchar(50),
    `code` varchar(20),
    `reply_code` varchar(20),
    `pin` varchar(20),
    `url` varchar(30),
    `media` varchar(20),
    `created_at` TIMESTAMP, 
    `timeout_at` TIMESTAMP, 
    `reply_ack` BOOL DEFAULT '0',
    `click_ack` BOOL DEFAULT '0',
    `source` varchar(20),
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


