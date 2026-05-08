import http from 'k6/http';
import { sleep } from 'k6';

export default function () {
  http.get('https://google.com'); // এখানে আপনার আসল ডোমেইন দিতে পারেন
  sleep(1);
}
