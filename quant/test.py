
def test_high_open():
    import argparse
    from tasks.high_open_2pct import HighOpen2PctTask
    
    parser = argparse.ArgumentParser(description='连续涨停高开2点策略')
    parser.add_argument('--dry-run', action='store_true', help='模拟运行模式（跳过等待竞价）')
    args = parser.parse_args()
    args.dry_run = True
    task = HighOpen2PctTask(dry_run=args.dry_run)
    task.execute()


def test_daily_data():
    from tasks.daily_data_download import DailyDataDownloadTask
    task = DailyDataDownloadTask()
    task.init_count = 100
    task.execute()

if __name__ == '__main__':
    # test_high_open()
    test_daily_data()
