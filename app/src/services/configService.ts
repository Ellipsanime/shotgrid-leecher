import {loadConfig} from "../tools/config";
import axios from "axios";
import {CommonHeaders, toFailure} from "../tools/requests";
import {Failure} from "../records/forms";


export async function fetchCredentials(): Promise<string[] | Failure> {
  const apiUrl = loadConfig().activeUri;
  const url = `${apiUrl}/config/credentials`;
  try {
    const response = await axios.get(url, {headers: CommonHeaders});
    return response?.data || []
  } catch (e: any) {
    return toFailure(e);
  }
}
