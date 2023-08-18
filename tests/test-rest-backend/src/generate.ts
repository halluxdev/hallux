interface dbRecords {
  [key: string]: string;
}
import db from './db.json';
import crypto from 'crypto';


const records = db as dbRecords;

export default async function generate(prompt: string) {
  return new Promise<string>((resolve, reject) => {
    // console.log(prompt);
    const md5sum = crypto.createHash('md5');
    const hash = md5sum.update(prompt).digest('hex');
    const result = records[hash];
    console.log(hash);

    if (result) {
      resolve(result);
    } else {
      reject(new Error('No result found'));
    }
  });
}