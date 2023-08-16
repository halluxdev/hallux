interface dbRecords {
  [key: string]: string;
}
import db from './db.json';

const records = db as dbRecords;

export default async function generate(prompt: string) {
  return new Promise<string>((resolve, reject) => {
    const result = records[prompt];
    if (result) {
      resolve(result);
    } else {
      reject(new Error('No result found'));
    }
  });
}