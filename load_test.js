import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  vus: 10, // ১০ জন ভার্চুয়াল ইউজার
  duration: '10s', // ১০ সেকেন্ড ধরে টেস্ট চলবে
};

export default function () {
  http.get('https://google.com'); // এখানে আপনার আসল API বা ওয়েবসাইটের লিঙ্ক দিন
  sleep(1);
}
